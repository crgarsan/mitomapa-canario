// Temporary compatibility for the pinned deploy-pages v5.0.1 dependency graph.
// Scoped to that action process; all other imports and warnings stay unchanged.
// Remove this preload once an upstream release passes check_pages_runtime.py.
import { registerHooks } from 'node:module';

const replacement = new URL('./pages-punycode-exports.js', import.meta.url).href;
registerHooks({
  resolve(specifier, context, nextResolve) {
    if (specifier === 'punycode' || specifier === 'node:punycode') {
      return { url: replacement, format: 'commonjs', shortCircuit: true };
    }
    return nextResolve(specifier, context);
  }
});
