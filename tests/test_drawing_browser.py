"""Exercise progress imports and persisted drawings in a real local browser.

Requires Python Playwright, Pillow and Chromium; does not contact Cloudflare.
"""
import base64
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import io
import json
from pathlib import Path
import shutil
import struct
import threading
import unittest
import zlib

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
STORAGE = "mitomapa-canario-cuaderno-v1"


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


def image_url(fmt="PNG", *, transparent=False, lossless=False):
    image = Image.new("RGBA", (900, 520), (155, 87, 56, 255))
    if transparent:
        image.putpixel((0, 0), (0, 0, 0, 0))
    output = io.BytesIO()
    image.save(output, format=fmt, lossless=lossless)
    mime = "png" if fmt == "PNG" else "webp"
    return f"data:image/{mime};base64," + base64.b64encode(output.getvalue()).decode()


def png_chunk(tag, payload):
    body = tag + payload
    return struct.pack(">I", len(payload)) + body + struct.pack(">I", zlib.crc32(body))


def hostile_png(width=100000, height=100000, *, animation=False, damaged=False):
    header = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    chunks = [png_chunk(b"IHDR", header)]
    if animation:
        chunks.append(png_chunk(b"acTL", struct.pack(">II", 100000, 0)))
    chunks += [png_chunk(b"IDAT", b"\x00\x00\x00\x00" if damaged else zlib.compress(b"\x00")), png_chunk(b"IEND", b"")]
    return "data:image/png;base64," + base64.b64encode(b"\x89PNG\r\n\x1a\n" + b"".join(chunks)).decode()


def undecodable_webp():
    header = bytearray(10)
    header[3:6] = b"\x9d\x01\x2a"
    struct.pack_into("<HH", header, 6, 900, 520)
    chunk = b"VP8 " + struct.pack("<I", len(header)) + header
    raw = b"RIFF" + struct.pack("<I", 4 + len(chunk)) + b"WEBP" + chunk
    return "data:image/webp;base64," + base64.b64encode(raw).decode()


def payload(drawing=None, name="Antes"):
    return {
        "app": "mitomapa-canario", "learningLevel": "advanced", "learnerName": name,
        "progress": {"sourcePassed": ["tenerife"], "truthPassed": [], "earned": []},
        "workshop": {"routes": {"gran-canaria": {"drawing": drawing, "drawingHasInk": bool(drawing), "creation": bool(drawing)}}},
    }


SOURCE_SPY = """
window.__drawingSources=[];
const descriptor=Object.getOwnPropertyDescriptor(HTMLImageElement.prototype,"src");
Object.defineProperty(HTMLImageElement.prototype,"src",{
 configurable:true,get:descriptor.get,set(value){
  if(String(value).startsWith("data:"))window.__drawingSources.push(value);
  descriptor.set.call(this,value);
 }
});
window.confirm=()=>true;
"""


class DrawingBrowserTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(ROOT)))
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}/"
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(
            executable_path=shutil.which("chromium"),
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def setUp(self):
        self.context = self.browser.new_context()
        self.context.add_init_script(SOURCE_SPY)
        self.page = self.context.new_page()
        self.errors = []
        self.page.on("pageerror", lambda error: self.errors.append(str(error)))
        self.page.goto(self.base, wait_until="networkidle")

    def tearDown(self):
        self.context.close()
        self.assertEqual(self.errors, [])

    def imported(self, value):
        self.page.locator("#importProgressFile").set_input_files(
            {"name": "seguimiento.json", "mimeType": "application/json", "buffer": json.dumps(value).encode()}
        )
        self.page.wait_for_function("""()=>{
         const text=document.getElementById("teacherImportStatus").textContent;
         return text.includes("correctamente")||text.startsWith("No se pudo cargar");
        }""")
        return self.page.locator("#teacherImportStatus").text_content()

    def test_unsafe_import_is_atomic_and_never_reaches_decoder(self):
        self.assertIn("correctamente", self.imported(payload()))
        before = self.page.evaluate("JSON.stringify({...localStorage})")
        for drawing in [hostile_png(), hostile_png(901, 1), hostile_png(900, 520, animation=True)]:
            self.page.evaluate('document.getElementById("teacherImportStatus").textContent=""')
            self.assertIn("dibujo", self.imported(payload(drawing, "Después")))
            self.assertEqual(self.page.evaluate("JSON.stringify({...localStorage})"), before)
            self.assertEqual(self.page.evaluate("window.__drawingSources"), [])
        # The damaged but bounded header passes the preflight and fails decoding.
        self.page.evaluate('document.getElementById("teacherImportStatus").textContent=""')
        self.assertIn("dibujo", self.imported(payload(undecodable_webp(), "Después")))
        self.assertEqual(self.page.evaluate("JSON.stringify({...localStorage})"), before)

    def test_native_png_and_webp_variants_normalize_and_restore(self):
        for drawing in [
            image_url(), image_url("WEBP"), image_url("WEBP", transparent=True),
            image_url("WEBP", lossless=True), image_url("WEBP", transparent=True, lossless=True),
        ]:
            self.page.evaluate('document.getElementById("teacherImportStatus").textContent=""')
            self.assertIn("correctamente", self.imported(payload(drawing)))
            stored = self.page.evaluate("(key)=>JSON.parse(localStorage.getItem(key)).routes['gran-canaria']", STORAGE)
            self.assertTrue(stored["drawingHasInk"])
            self.assertTrue(self.page.evaluate("(value)=>Boolean(drawingImageSize(value))", stored["drawing"]))
            self.page.goto(self.base + "#isla/gran-canaria/taller", wait_until="networkidle")
            self.page.wait_for_function("""()=>{
             const canvas=document.querySelector("#activity-gran-canaria canvas");
             if(!canvas)return false;
             const color=canvas.getContext("2d").getImageData(20,20,1,1).data;
             return color[0]>140&&color[0]<170&&color[1]>70&&color[1]<105;
            }""")
            self.assertEqual(self.page.evaluate("(key)=>JSON.parse(localStorage.getItem(key)).routes['gran-canaria'].drawing", STORAGE), stored["drawing"])

    def test_drawing_undo_clear_and_export_remain_usable(self):
        self.assertIn("correctamente", self.imported(payload(image_url())))
        self.page.evaluate('location.hash="#isla/gran-canaria/taller"')
        self.page.locator("#activity-gran-canaria [data-activity-tab=creation]").click()
        canvas = self.page.locator("#activity-gran-canaria canvas")
        canvas.scroll_into_view_if_needed()
        original = self.page.evaluate("(key)=>JSON.parse(localStorage.getItem(key)).routes['gran-canaria'].drawing", STORAGE)
        box = canvas.bounding_box()
        self.page.mouse.move(box["x"] + 40, box["y"] + 40)
        self.page.mouse.down()
        self.page.mouse.move(box["x"] + 90, box["y"] + 90)
        self.page.mouse.up()
        self.page.locator("#activity-gran-canaria .draw-undo").click()
        self.page.wait_for_function("""()=>{
         const pixel=document.querySelector("#activity-gran-canaria canvas").getContext("2d").getImageData(60,60,1,1).data;
         return pixel[0]>140&&pixel[0]<170;
        }""")
        restored = self.page.evaluate("(key)=>JSON.parse(localStorage.getItem(key)).routes['gran-canaria'].drawing", STORAGE)
        self.assertTrue(self.page.evaluate("(value)=>Boolean(drawingImageSize(value))", restored))
        self.assertEqual(self.page.evaluate("""()=>{
         const pixel=document.querySelector("#activity-gran-canaria canvas").getContext("2d").getImageData(60,60,1,1).data;
         return pixel[0]>140&&pixel[0]<170;
        }"""), True)
        self.assertIsNotNone(original)
        self.page.locator("#activity-gran-canaria .draw-clear").click()
        with self.page.expect_download() as download:
            self.page.evaluate("exportProgress()")
        exported = json.loads(Path(download.value.path()).read_text())
        self.assertIsNone(exported["workshop"]["routes"]["gran-canaria"]["drawing"])
        self.assertFalse(exported["workshop"]["routes"]["gran-canaria"]["drawingHasInk"])

    def test_previous_unsafe_storage_is_purged_before_decode_and_on_reload(self):
        unsafe = hostile_png()
        self.page.evaluate("""({key,unsafe})=>{
         localStorage.setItem(key,JSON.stringify({routes:{"gran-canaria":{drawing:unsafe,drawingHasInk:true,creation:true,text:"",words:true}}}));
        }""", {"key": STORAGE, "unsafe": unsafe})
        for _ in range(2):
            self.page.reload(wait_until="networkidle")
            stored = self.page.evaluate("(key)=>JSON.parse(localStorage.getItem(key)).routes['gran-canaria']", STORAGE)
            self.assertIsNone(stored["drawing"])
            self.assertFalse(stored["drawingHasInk"])
            self.assertFalse(stored["creation"])
            self.assertTrue(stored["words"])
            self.assertNotIn(unsafe, self.page.evaluate("window.__drawingSources"))


if __name__ == "__main__":
    unittest.main()
