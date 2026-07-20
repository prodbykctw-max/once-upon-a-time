import http.server, socketserver, base64, os, sys

# Dev server: serves the repo + accepts POST /save?name=x.jpg with a data-URL
# body, writing it to tools/captures/. Lets the GL testbed save frames to disk.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAPS = os.path.join(ROOT, 'tools', 'captures')
os.makedirs(CAPS, exist_ok=True)

# rAF shim for hidden-tab verification: replaces requestAnimationFrame with a
# timer-driven pump so the game loop advances even when the pane is hidden.
SHIM = (b"<script>(function(){window.__err=[];window.addEventListener('error',function(e){"
        b"window.__err.push((e.message||'')+' @'+(e.lineno||0)+':'+(e.colno||0));});"
        b"var q=[];window.requestAnimationFrame=function(cb){"
        b"q.push(cb);return q.length;};function pump(){var c=q;q=[];var t=performance.now();"
        b"for(var i=0;i<c.length;i++){try{c[i](t)}catch(e){"
        b"window.__err.push('RAF '+(e&&e.message)+' | '+String(e&&e.stack).slice(0,300));}}"
        b"setTimeout(pump,33);}pump();})();</script>")

class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def end_headers(self):
        # The http-server this replaced ran with -c-1 (caching off). Without
        # this, SimpleHTTPRequestHandler sends Last-Modified and answers
        # If-Modified-Since with 304, so the browser keeps serving a stale
        # index.html and you appear to be testing an old build.
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def send_header(self, k, v):
        if k.lower() == 'last-modified':
            return          # suppress: it is what enables the 304 path
        super().send_header(k, v)

    def do_GET(self):
        if self.path.startswith('/index.html') and 'shim=1' in self.path:
            with open(os.path.join(ROOT, 'index.html'), 'rb') as f:
                body = f.read()
            body = body.replace(b'<script>', SHIM + b'<script>', 1)
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()

    def do_POST(self):
        if self.path.startswith('/save'):
            from urllib.parse import urlparse, parse_qs
            q = parse_qs(urlparse(self.path).query)
            name = os.path.basename(q.get('name', ['cap.jpg'])[0])
            n = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(n).decode('utf-8')
            if ',' in body:
                body = body.split(',', 1)[1]
            with open(os.path.join(CAPS, name), 'wb') as f:
                f.write(base64.b64decode(body))
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'saved')
        else:
            self.send_response(404); self.end_headers()

    def log_message(self, *a):
        pass

# Port: explicit argv wins, else the harness-assigned PORT env var, else 9123.
# Honouring PORT is what lets launch.json use "autoPort" and dodge collisions.
port = int(sys.argv[1]) if len(sys.argv) > 1 else int(os.environ.get('PORT', 9123))
with socketserver.ThreadingTCPServer(('127.0.0.1', port), H) as srv:
    srv.allow_reuse_address = True
    print(f'devserver on {port}')
    srv.serve_forever()
