#!/usr/bin/env python3
"""Pre-deploy gate: NO STOCK GLYPHS IN GAME UI (client directive, regressed twice).
Fails if index.html ships symbol/emoji characters outside code comments.
Typography stays allowed: accents (Jande), dashes, quotes, ellipsis, middle dot,
multiplication sign, degree, approx, plus-minus."""
import re,sys

src=open('index.html',encoding='utf-8').read()
# strip /* ... */ blocks, then strip // line comments (but not http:// or https://)
src=re.sub(r'/\*.*?\*/','',src,flags=re.S)
src=re.sub(r'(?<!:)//[^\n]*','',src)
# also strip HTML comments
src=re.sub(r'<!--.*?-->','',src,flags=re.S)

BAD_RANGES=[(0x2190,0x21FF),  # arrows
            (0x2300,0x23FF),  # misc technical (pause bars etc.)
            (0x25A0,0x25FF),  # geometric shapes (pips, play triangles)
            (0x2600,0x27BF),  # misc symbols + dingbats (gears, flags, sparkles, checks)
            (0x2660,0x266F),  # (covered above; explicit for music notes)
            (0x1F000,0x1FAFF)]# emoji
ALLOW=set('—–‘’“”…·×°≈±')
bad={}
line=1
for ch in src:
    if ch=='\n': line+=1; continue
    o=ord(ch)
    if o<128 or ch in ALLOW: continue
    if ch in 'éÉèàçüöñÈ': continue
    if any(a<=o<=b for a,b in BAD_RANGES) or o>0x2000 and ch not in ALLOW and not (0x2500<=o<=0x257F):
        bad.setdefault(ch,[]).append(line)
if bad:
    print('ABORT: stock glyphs in shipped code (NO STOCK GLYPHS directive):')
    for ch,lines in bad.items():
        print('  %r U+%04X  lines %s'%(ch,ord(ch),lines[:5]))
    sys.exit(1)
print('glyph gate: clean')
