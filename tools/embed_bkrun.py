import base64, io, os, re
from PIL import Image

# Swap the Temple View run sprite (SPRITES.bkrun.src) for the new AutoSprite
# straight-behind run. The old one was a SIDE PROFILE, so dropped into the
# behind-the-back corridor it read as tilted and lurching. This one is a true
# running-away-from-camera view (iso_run_up): upright, centred, even gait.
# Already a 5x5 grid of 256px frames with a transparent background, so it drops
# straight into the existing 25-frame/5-col spec with no re-layout.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'assets', 'renders', 'jande_as', 'bkrun_up.png')

im = Image.open(SRC).convert('RGBA')
assert im.size == (1280, 1280), 'unexpected sheet size ' + str(im.size)
b = io.BytesIO()
im.save(b, 'WEBP', quality=88, method=6)
payload = 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()
print(f'bkrun sheet -> {len(b.getvalue())//1024} KB')

idx = os.path.join(ROOT, 'index.html')
s = io.open(idx, encoding='utf-8').read()
# replace only the src inside the bkrun spec, leave frames/cw/ch/cols alone
m = re.search(r"(bkrun:\{[^}]*?src:')(data:image/[^']*)(')", s)
assert m, 'bkrun.src not found'
s = s[:m.start(2)] + payload + s[m.end(2):]
io.open(idx, 'w', encoding='utf-8', newline='\n').write(s)
print('index.html now', len(s) // 1024, 'KB')
