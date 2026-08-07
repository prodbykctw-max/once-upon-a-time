import io, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
idx = os.path.join(ROOT, 'index.html')
src = io.open(idx, encoding='utf-8').read()
engine = io.open(os.path.join(ROOT, 'tools', 'glworld_engine.js'), encoding='utf-8').read()
data = io.open(os.path.join(ROOT, 'tools', 'glwdata.js'), encoding='utf-8').read()

assert 'var GLWORLD' not in src, 'already inserted'
marker = 'function drawT(){'
assert src.count(marker) == 1, 'marker count %d' % src.count(marker)
block = data + '\n' + engine + '\n'
src = src.replace(marker, block + marker)
io.open(idx, 'w', encoding='utf-8', newline='\n').write(src)
print('inserted', len(block) // 1024, 'KB; new size', len(src) // 1024, 'KB')
