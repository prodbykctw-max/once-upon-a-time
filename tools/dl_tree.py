import json, os, urllib.request

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64) AppleWebKit/537.36 Chrome/120'}
DEST = r"C:\Users\Owner\Documents\once-upon-a-time\assets\models\island_tree_01"
os.makedirs(DEST, exist_ok=True)


def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120).read()


files = json.loads(get('https://api.polyhaven.com/files/island_tree_01'))
g = files['gltf']['1k']['gltf']
todo = {g['url'].split('/')[-1]: g['url']}
for rel, meta in g.get('include', {}).items():
    todo[rel.replace('\\', '/')] = meta['url']

for rel, url in todo.items():
    dest = os.path.join(DEST, os.path.basename(rel))
    with open(dest, 'wb') as f:
        f.write(get(url))
    print('got', os.path.basename(rel), os.path.getsize(dest) // 1024, 'KB')
print('DL_DONE')
