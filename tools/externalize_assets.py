"""Externalize embedded base64 assets from index.html into web/ binary files.

The game embeds ~3 MB of images/fonts as data: URIs inline. Every consumer loads
them via `img.src = <string>` or CSS `url(<string>)`, so swapping the data: URI
for a relative URL is a safe drop-in — the browser fetches the binary instead.

Wins: no base64 inflation (~33% smaller on the wire), per-asset browser caching,
parallel/lazy loading, and git can finally delta-compress (editing one prop no
longer rewrites a 4.4 MB text blob).

Filenames are content-addressed (sha1[:12]) so identical blobs dedup to one file
and an unchanged asset keeps its name across rebuilds = perfect cache key.
Tiny blobs (< THRESH) stay inline — not worth an extra request.
"""
import io, os, re, base64, hashlib

ROOT = r"C:\Users\Owner\Documents\once-upon-a-time"
IDX = os.path.join(ROOT, 'index.html')
WEB = os.path.join(ROOT, 'web')
os.makedirs(WEB, exist_ok=True)

EXT = {'image/webp': 'webp', 'image/png': 'png', 'image/jpeg': 'jpg', 'image/jpg': 'jpg',
       'image/gif': 'gif', 'image/svg+xml': 'svg', 'font/ttf': 'ttf', 'font/woff2': 'woff2',
       'font/woff': 'woff', 'application/font-woff': 'woff', 'audio/mpeg': 'mp3', 'audio/wav': 'wav'}
THRESH = 1024   # bytes (decoded); below this, keep inline

s = io.open(IDX, encoding='utf-8').read()
orig_len = len(s)
pat = re.compile(r'data:([a-zA-Z0-9.+/-]+);base64,([A-Za-z0-9+/=]+)')

seen = {}          # filename -> True
manifest = []      # (filename, mime, bytes)
stats = {'ext': 0, 'kept': 0, 'bytes': 0}


def repl(m):
    mime, b64 = m.group(1), m.group(2)
    try:
        raw = base64.b64decode(b64)
    except Exception:
        return m.group(0)                       # leave anything unparseable inline
    if len(raw) < THRESH:
        stats['kept'] += 1
        return m.group(0)
    ext = EXT.get(mime, 'bin')
    h = hashlib.sha1(raw).hexdigest()[:12]
    fn = f'{h}.{ext}'
    if fn not in seen:
        open(os.path.join(WEB, fn), 'wb').write(raw)
        seen[fn] = True
        manifest.append((fn, mime, len(raw)))
        stats['ext'] += 1
        stats['bytes'] += len(raw)
    return 'web/' + fn


new = pat.sub(repl, s)
io.open(IDX, 'w', encoding='utf-8', newline='\n').write(new)

# debug manifest (not served)
manifest.sort(key=lambda r: -r[2])
with io.open(os.path.join(WEB, '_manifest.txt'), 'w', encoding='utf-8', newline='\n') as f:
    for fn, mime, n in manifest:
        f.write(f'{n:>9}  {mime:12s}  {fn}\n')

print(f'externalized {stats["ext"]} unique files, {stats["bytes"]/1048576:.2f} MB written to web/')
print(f'kept {stats["kept"]} tiny blobs inline')
print(f'index.html: {orig_len/1048576:.2f} MB -> {len(new)/1048576:.2f} MB')
# sanity: remaining data: URIs should equal the tiny ones we kept
print(f'data: URIs remaining in index.html: {len(pat.findall(new))}')
