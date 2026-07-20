import json, os, urllib.request

# CC0 HDRIs from Poly Haven for image-based lighting — the realism win that
# point/area lamps cannot give: real sky gradients, correct sun angle and
# colour, and true environment reflections. One per stage, matched to that
# world's time of day in the whimsy day-cycle.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'assets', 'hdri')
os.makedirs(OUT, exist_ok=True)
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36'}

PICKS = [
    (0, 'glasshouse_interior', 'library'),    # sun through a glazed roof
    (1, 'kiara_1_dawn',        'meadow'),     # FIRST LIGHT
    (2, 'kiara_3_morning',     'blossom'),
    (3, 'borghese_gardens',    'rose'),       # formal garden, bright day
    (4, 'lakeside_dawn',       'lake'),       # THE MIRROR LAKE
    (5, 'epping_forest_01',    'glade'),      # dappled woodland
    (6, 'golden_gate_hills',   'sunflower'),  # THE GOLDEN HOUR
    (7, 'cloud_layers',        'clouds'),     # above the clouds
    (8, 'dikhololo_sunset',    'sunset'),     # HER ENCORE
]
RES = '1k'   # plenty for lighting; we never see the backdrop (transparent film)


def get_json(u):
    return json.load(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60))


total = 0
for idx, asset, short in PICKS:
    dest = os.path.join(OUT, f'{short}.hdr')
    if os.path.exists(dest) and os.path.getsize(dest) > 10240:
        print(f'{idx} {short:10s} cached')
        total += os.path.getsize(dest)
        continue
    try:
        files = get_json(f'https://api.polyhaven.com/files/{asset}')
        node = files['hdri'][RES]
        entry = node.get('hdr') or node.get('exr')
        req = urllib.request.Request(entry['url'], headers=UA)
        with urllib.request.urlopen(req, timeout=300) as r, open(dest, 'wb') as f:
            f.write(r.read())
        sz = os.path.getsize(dest)
        total += sz
        print(f'{idx} {short:10s} <- {asset:22s} {sz//1024} KB')
    except Exception as e:
        print(f'{idx} {short:10s} FAILED ({asset}): {type(e).__name__} {e}')

print(f'\ntotal {total//1024//1024} MB -> {OUT}')
