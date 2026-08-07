import json, os, sys, urllib.request

# Pull CC0 PBR texture sets from Poly Haven for the nine stage grounds.
# CC0 = public domain: no attribution, safe for a commercial release.
# Blender's Poly Haven addon does exactly this over its own bridge; we go
# straight to the same public API so the whole pipeline stays headless.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'assets', 'pbr')
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36'}

# stage index -> (poly haven asset id, our short name)
PICKS = [
    (0, 'herringbone_parquet', 'library'),   # grand hall parquet
    (1, 'leafy_grass',         'meadow'),
    (2, 'grass_path_2',        'blossom'),   # a promenade path through grass
    (3, 'sparse_grass',        'rose'),      # clipped garden lawn
    (4, 'coast_sand_01',       'lake'),
    (5, 'forrest_ground_01',   'glade'),     # mossy forest floor
    (6, 'dirt',                'sunflower'), # dry field earth
    (7, 'marble_01',           'clouds'),
    (8, 'cobblestone_05',      'sunset'),
]
# map key in the API -> filename we save it as
MAPS = {'Diffuse': 'diff', 'nor_gl': 'nor', 'Rough': 'rough', 'Displacement': 'disp'}
RES = '1k'


def get_json(url):
    return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60))


def fetch(url, dest):
    if os.path.exists(dest) and os.path.getsize(dest) > 1024:
        return 'cached'
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=180) as r, open(dest, 'wb') as f:
        f.write(r.read())
    return f'{os.path.getsize(dest)//1024} KB'


total = 0
for idx, asset, short in PICKS:
    d = os.path.join(OUT, short)
    os.makedirs(d, exist_ok=True)
    try:
        files = get_json(f'https://api.polyhaven.com/files/{asset}')
    except Exception as e:
        print(f'{short:10s} FAILED to list: {e}')
        continue
    got = []
    for api_key, tag in MAPS.items():
        node = files.get(api_key)
        if not node:
            continue
        # some maps nest per-resolution then per-format
        res = node.get(RES) or node.get('1k')
        if not res:
            continue
        entry = res.get('jpg') or res.get('png')
        if not entry:
            continue
        dest = os.path.join(d, f'{tag}.jpg' if entry is res.get('jpg') else f'{tag}.png')
        try:
            info = fetch(entry['url'], dest)
            got.append(f'{tag}({info})')
            total += os.path.getsize(dest)
        except Exception as e:
            print(f'  {short}/{tag} failed: {e}')
    print(f'{idx} {short:10s} <- {asset:22s} {" ".join(got)}')

print(f'\ntotal {total//1024//1024} MB -> {OUT}')
