'use strict';

// Test harness only: the action is loaded intact with no GitHub environment.
// All network entry points throw before they can contact any service.
const Module = require('node:module');
const networkAttempts = [];
const punycodeLoads = [];
const warnings = [];

function blocked(name) {
  return function () {
    networkAttempts.push(name);
    throw new Error('NETWORK_BLOCKED:' + name);
  };
}

const net = require('node:net');
net.Socket.prototype.connect = blocked('net.Socket.connect');
net.connect = blocked('net.connect');
net.createConnection = blocked('net.createConnection');
require('node:tls').connect = blocked('tls.connect');
for (const name of ['node:http', 'node:https']) {
  require(name).request = blocked(name + '.request');
  require(name).get = blocked(name + '.get');
}
const dns = require('node:dns');
for (const surface of [dns, dns.promises, dns.Resolver.prototype, dns.promises.Resolver.prototype]) {
  for (const name of Object.getOwnPropertyNames(surface)) {
    if (/^(lookup|resolve|reverse)/.test(name) && typeof surface[name] === 'function') {
      surface[name] = blocked('dns.' + name);
    }
  }
}
globalThis.fetch = blocked('fetch');

const originalLoad = Module._load;
Module._load = function (specifier, parent, isMain) {
  const loaded = originalLoad.call(this, specifier, parent, isMain);
  if (specifier === 'punycode' || specifier === 'node:punycode') {
    punycodeLoads.push({specifier, version: loaded.version});
  }
  return loaded;
};
process.on('warning', warning => warnings.push({code: warning.code, message: warning.message}));

let failure = null;
try {
  require(process.argv[2]);
} catch (error) {
  failure = {message: error.message};
  process.exitCode = 1;
}

// The normal warning handler must still write this independent deprecation.
process.emitWarning('Pages runtime smoke warning probe', {
  type: 'DeprecationWarning', code: 'MITOMAPA_SMOKE'
});
setImmediate(() => {
  console.log(JSON.stringify({
    node: process.version, failure, networkAttempts, punycodeLoads, warnings
  }));
});
