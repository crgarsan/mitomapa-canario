const {test}=require("node:test");
const assert=require("node:assert/strict");
const fs=require("node:fs");
const vm=require("node:vm");
const {deflateSync}=require("node:zlib");

const source=fs.readFileSync(require("node:path").join(__dirname,"../scripts.js"),"utf8");
const helpers=source.slice(source.indexOf("// Comprueba los contenedores completos"),source.indexOf('const workshopStorageKey='));
const crc=bytes=>{
 let value=0xffffffff;
 for(const byte of bytes){value^=byte;for(let bit=0;bit<8;bit++)value=(value>>>1)^((value&1)?0xedb88320:0);}
 return (value^0xffffffff)>>>0;
};
const pngChunk=(type,data=Buffer.alloc(0))=>{
 const chunk=Buffer.alloc(data.length+12);chunk.writeUInt32BE(data.length);chunk.write(type,4);data.copy(chunk,8);
 chunk.writeUInt32BE(crc(chunk.subarray(4,-4)),chunk.length-4);return chunk;
};
const png=(width=900,height=520,extra=[])=>{
 const header=Buffer.alloc(13);header.writeUInt32BE(width);header.writeUInt32BE(height,4);header[8]=8;header[9]=6;
 // Only the ordinary fixture needs valid pixels; never expand the hostile dimensions.
 const pixels=width<=900&&height<=520?Buffer.alloc((width*4+1)*height):Buffer.from([0]);
 return Buffer.concat([Buffer.from([137,80,78,71,13,10,26,10]),pngChunk("IHDR",header),...extra,pngChunk("IDAT",deflateSync(pixels)),pngChunk("IEND")]);
};
const data=(bytes,mime="png")=>"data:image/"+mime+";base64,"+bytes.toString("base64");
const riffChunk=(type,payload)=>{
 const chunk=Buffer.alloc(8+payload.length+(payload.length&1));chunk.write(type);chunk.writeUInt32LE(payload.length,4);payload.copy(chunk,8);return chunk;
};
const webp=chunks=>{
 const payload=Buffer.concat(chunks),header=Buffer.alloc(12);header.write("RIFF");header.writeUInt32LE(payload.length+4,4);header.write("WEBP",8);return Buffer.concat([header,payload]);
};
const vp8=(width=900,height=520)=>{
 const bytes=Buffer.alloc(10);bytes[3]=157;bytes[4]=1;bytes[5]=42;bytes.writeUInt16LE(width,6);bytes.writeUInt16LE(height,8);return riffChunk("VP8 ",bytes);
};
const vp8l=(width=900,height=520)=>{
 const bytes=Buffer.alloc(5);bytes[0]=47;bytes.writeUInt32LE(((width-1)|((height-1)<<14))>>>0,1);return riffChunk("VP8L",bytes);
};
const vp8x=(width=900,height=520,flags=0)=>{
 const bytes=Buffer.alloc(10);bytes[0]=flags;bytes.writeUIntLE(width-1,4,3);bytes.writeUIntLE(height-1,7,3);return riffChunk("VP8X",bytes);
};
const nativePNG=data(png());
function runtime(overrides={}){
 const context={atob,Image:class{set src(value){throw new Error("Unexpected decoder: "+value.slice(0,40));}},...overrides};
 return vm.runInNewContext(helpers+";({drawingImageSize,safeWorkshopDrawing,removeUnsafeWorkshopDrawings,loadWorkshopDrawing,normalizeImportedDrawings})",context);
}
const api=runtime();
function dimensions(value){const size=api.drawingImageSize(value);return size?{width:size.width,height:size.height}:null;}

test("native PNG and smaller static PNG remain supported",()=>{
 assert.deepEqual(dimensions(nativePNG),{width:900,height:520});
 assert.deepEqual(dimensions(data(png(100,100))),{width:100,height:100});
});
test("static WebP VP8, VP8L and extended alpha headers remain supported",()=>{
 for(const chunks of [[vp8()],[vp8l()],[vp8x(),vp8()],[vp8x(),vp8l()],[vp8x(900,520,16),riffChunk("ALPH",Buffer.from([1,0])),vp8()]]){
  assert.deepEqual(dimensions(data(webp(chunks),"webp")),{width:900,height:520});
 }
});
test("oversized and zero PNG dimensions are rejected without decoding",async()=>{
 for(const [width,height] of [[100000,100000],[901,1],[1,521],[0,520],[900,0]]){
  const value=data(png(width,height));assert.equal(dimensions(value),null);assert.equal(await api.loadWorkshopDrawing(value),null);
 }
});
test("oversized lossy, lossless and extended WebP dimensions are rejected",()=>{
 for(const chunks of [[vp8(901,520)],[vp8l(900,521)],[vp8x(100000,100000),vp8()],[vp8x(),vp8(901,520)],[vp8x(),vp8l(900,521)]]){
  assert.equal(dimensions(data(webp(chunks),"webp")),null);
 }
});
test("declared WebP canvas and raster dimensions must match",()=>{
 for(const payload of [vp8(899,520),vp8l(900,519)])assert.equal(dimensions(data(webp([vp8x(),payload]),"webp")),null);
});
test("bounded uncompressed WebP color profiles are supported, oversized profiles are rejected",()=>{
 const profile=Buffer.alloc(132);profile.writeUInt32BE(132);profile.write("acsp",36);
 assert.deepEqual(dimensions(data(webp([vp8x(900,520,32),riffChunk("ICCP",profile),vp8()]),"webp")),{width:900,height:520});
 const huge=Buffer.alloc(4097);huge.writeUInt32BE(4097);huge.write("acsp",36);
 for(const chunks of [[vp8x(900,520,32),riffChunk("ICCP",huge),vp8()],[vp8x(900,520,32),vp8()],[vp8x(),riffChunk("ICCP",profile),vp8()]]){
  assert.equal(dimensions(data(webp(chunks),"webp")),null);
 }
});
test("MIME mismatch, external URLs and malformed or oversized base64 are rejected",()=>{
 const validWebP=webp([vp8()]);
 for(const value of [data(png(),"webp"),data(validWebP,"png"),"https://example.test/image.png","data:image/svg+xml;base64,AAAA",nativePNG+"!","data:image/png;base64,AA=",nativePNG.slice(0,-4),"data:image/png;base64,"+"A".repeat(2500000)]){
  assert.equal(dimensions(value),null);
 }
});
test("PNG animations and compressed metadata are rejected",()=>{
 for(const type of ["acTL","fcTL","fdAT","iCCP","zTXt","iTXt"])assert.equal(dimensions(data(png(900,520,[pngChunk(type,Buffer.alloc(12))]))),null);
});
test("WebP animations are rejected with and without the animation flag",()=>{
 for(const chunks of [[vp8x(900,520,2),vp8()],[vp8x(),riffChunk("ANIM",Buffer.alloc(6)),vp8()],[vp8x(),riffChunk("ANMF",Buffer.alloc(16)),vp8()]]){
  assert.equal(dimensions(data(webp(chunks),"webp")),null);
 }
});
test("PNG duplicates, missing terminators, trailing bytes and invalid CRC are rejected",()=>{
 const valid=png(),header=valid.subarray(8,33),invalidCRC=Buffer.from(valid);invalidCRC[29]^=1;
 for(const bytes of [Buffer.concat([valid.subarray(0,33),header,valid.subarray(33)]),valid.subarray(0,-12),Buffer.concat([valid,Buffer.from([0])]),invalidCRC]){
  assert.equal(dimensions(data(bytes)),null);
 }
});
test("PNG and WebP out-of-range chunk lengths are rejected",()=>{
 const brokenPNG=png();brokenPNG.writeUInt32BE(0xffffffff,33);
 const brokenWebP=webp([vp8()]);brokenWebP.writeUInt32LE(0xffffffff,16);
 assert.equal(dimensions(data(brokenPNG)),null);assert.equal(dimensions(data(brokenWebP,"webp")),null);
});
test("WebP duplicate payloads, RIFF mismatch, invalid padding and reserved flags are rejected",()=>{
 const wrongSize=webp([vp8()]);wrongSize.writeUInt32LE(wrongSize.length,4);
 const odd=webp([vp8l()]);odd[odd.length-1]=1;
 for(const bytes of [webp([vp8(),vp8()]),webp([vp8(),vp8l()]),wrongSize,odd,webp([vp8x(900,520,128),vp8()]),webp([vp8x(900,520,16),vp8()])]){
  assert.equal(dimensions(data(bytes,"webp")),null);
 }
});
test("unsafe stored drawings are purged while ordinary learner state survives",()=>{
 const state={routes:{bad:{drawing:data(png(100000,100000)),drawingHasInk:true,creation:true,text:"",words:true},good:{drawing:nativePNG,drawingHasInk:true,creation:true,text:"Descripción"},text:{drawing:"https://example.test/image.png",drawingHasInk:true,creation:true,text:"Alternativa escrita"}}};
 assert.equal(api.removeUnsafeWorkshopDrawings(state),true);
 assert.equal(state.routes.bad.drawing,null);assert.equal(state.routes.bad.drawingHasInk,false);assert.equal(state.routes.bad.creation,false);assert.equal(state.routes.bad.words,true);
 assert.equal(state.routes.good.drawing,nativePNG);assert.equal(state.routes.good.creation,true);assert.equal(state.routes.text.creation,true);
 assert.equal(api.removeUnsafeWorkshopDrawings(state),false);
});
test("normalization bounds decode and re-encodes before returning imported state",async()=>{
 const decoded=[],output=data(png()),drawn=[];
 const normalizer=runtime({
  Image:class{set src(value){decoded.push(value);this.naturalWidth=100;this.naturalHeight=100;queueMicrotask(()=>this.onload());}},
  document:{createElement:()=>({getContext:()=>({fillRect(){},drawImage(...args){drawn.push(args);}}),toDataURL:()=>output})}
 });
 const clean={routes:{route:{drawing:data(png(100,100)),drawingHasInk:true}}};
 assert.equal(await normalizer.normalizeImportedDrawings(clean),clean);
 assert.equal(decoded.length,1);assert.equal(drawn[0][3],900);assert.equal(drawn[0][4],520);assert.equal(clean.routes.route.drawing,output);
});
test("decoder dimension disagreement and damaged bounded payload fail normalization",async()=>{
 for(const mode of ["mismatch","error"]){
  const normalizer=runtime({Image:class{set src(value){this.naturalWidth=901;this.naturalHeight=520;queueMicrotask(()=>mode==="error"?this.onerror():this.onload());}}});
  await assert.rejects(normalizer.normalizeImportedDrawings({routes:{route:{drawing:nativePNG}}}),/DRAWING_INVALID/);
 }
});
