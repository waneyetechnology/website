import os
import csscompressor
import jsmin

def minify_html(html: str) -> str:
    # Regex fallback for HTML minification (no htmlmin)
    import re
    html = re.sub(r'>\s+<', '><', html)
    html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
    html = re.sub(r'\s{2,}', ' ', html)
    return html.strip()

def minify_css(css: str) -> str:
    return csscompressor.compress(css)

def minify_js(js: str) -> str:
    return jsmin.jsmin(js)

def minify_file(filepath: str, minify_func):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    minified = minify_func(content)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(minified)

def minify_all():
    # Minify HTML files in root and src
    for fname in ['index.html']:
        path = os.path.join(os.path.dirname(__file__), '..', fname)
        if os.path.exists(path):
            minify_file(path, minify_html)
    # Minify CSS and JS in static
    static_dir = os.path.join(os.path.dirname(__file__), '..', 'static')
    css_path = os.path.join(static_dir, 'style.css')
    js_path = os.path.join(static_dir, 'main.js')
    if os.path.exists(css_path):
        minify_file(css_path, minify_css)
    if os.path.exists(js_path):
        minify_file(js_path, minify_js)
