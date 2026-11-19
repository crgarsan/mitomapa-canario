// Keep Node's named ESM exports while returning the unmodified CommonJS API.
// Explicit assignments let Node statically detect this facade's named exports.
const punycode = require('./vendor/punycode-2.3.1.js');
exports.version = punycode.version;
exports.ucs2 = punycode.ucs2;
exports.decode = punycode.decode;
exports.encode = punycode.encode;
exports.toASCII = punycode.toASCII;
exports.toUnicode = punycode.toUnicode;
module.exports = punycode;
