/* MitoMapa: context-aware rendering for native project metadata.
 * The sanitizer is private to the iDevice; no host DOMPurify global is changed.
 */
(function () {
    const module = { exports: {} };
    const exports = module.exports;
    /* DOMPURIFY_VENDOR */
    const purifier = module.exports;
    const text = value => String(value ?? '').replace(/[&<>"']/g, char => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    }[char]));

    function safeURL(value, kind) {
        if (typeof value !== 'string' || /[\u0000-\u001f\u007f]/.test(value)) return '';
        const raw = value.trim();
        if (!raw) return '';
        try {
            const url = new URL(raw, document.baseURI);
            if (url.protocol === 'http:' || url.protocol === 'https:') return url.href;
            if (url.protocol === 'file:' && location.protocol === 'file:') return url.href;
            if (kind === 'link' && ['mailto:', 'tel:'].includes(url.protocol)) return url.href;
            if (kind === 'image' && url.protocol === 'blob:' && url.origin === location.origin) return url.href;
            if (kind === 'image' && /^data:image\/(?:png|jpe?g|gif|webp|avif);base64,[a-z0-9+/=\s]+$/i.test(raw)) return raw;
        } catch (_) { /* Reject a malformed URL instead of rendering it. */ }
        return '';
    }

    const policy = {
        ALLOWED_TAGS: ['a', 'p', 'br', 'strong', 'b', 'em', 'i', 'u', 's', 'span',
            'sub', 'sup', 'small', 'code', 'pre', 'ul', 'ol', 'li', 'blockquote',
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'table', 'thead', 'tbody',
            'tfoot', 'tr', 'td', 'th', 'caption', 'img'],
        ALLOWED_ATTR: ['href', 'title', 'target', 'rel', 'alt', 'src', 'width',
            'height', 'colspan', 'rowspan', 'scope', 'lang', 'dir'],
        ALLOW_DATA_ATTR: false,
        ALLOW_ARIA_ATTR: false,
        ALLOW_UNKNOWN_PROTOCOLS: false,
        FORBID_TAGS: ['script', 'style', 'iframe', 'object', 'embed', 'svg', 'math',
            'form', 'input', 'button', 'textarea', 'select', 'option', 'template'],
        FORBID_CONTENTS: ['script', 'style', 'iframe', 'object', 'embed', 'svg', 'math', 'template'],
        FORBID_ATTR: ['style', 'id', 'name'],
        SANITIZE_DOM: true,
        SANITIZE_NAMED_PROPS: true,
        RETURN_TRUSTED_TYPE: false
    };
    if (purifier.isSupported) purifier.addHook('afterSanitizeAttributes', node => {
        for (const [attribute, kind] of [['href', 'link'], ['src', 'image']]) {
            if (!node.hasAttribute(attribute)) continue;
            const url = safeURL(node.getAttribute(attribute), kind);
            if (url) node.setAttribute(attribute, url);
            else node.removeAttribute(attribute);
        }
        if (node.nodeName === 'A' && node.getAttribute('target') === '_blank') {
            node.setAttribute('rel', 'noopener noreferrer');
        }
    });
    return Object.freeze({
        text,
        rich(value) {
            // Fail closed to literal text in unsupported DOM implementations.
            return purifier.isSupported ? purifier.sanitize(String(value ?? ''), policy) : text(value);
        },
        image(value) {
            const url = safeURL(value, 'image');
            return url ? text('url(' + JSON.stringify(url) + ')') : 'none';
        }
    });
})()
