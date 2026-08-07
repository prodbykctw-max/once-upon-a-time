import base64, io, os, re

# Embed Storyboo.TTF as the game font and retire the Google-Fonts Poppins.
# Self-contained base64 @font-face so the single-file game needs no external
# request. Then swap every 'Poppins' reference (CSS classes AND canvas
# FX.font strings) to 'Storyboo', keeping the existing sans-serif fallbacks.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TTF = r"C:\Users\Owner\AppData\Local\Temp\Storyboo.TTF"

raw = open(TTF, 'rb').read()
b64 = base64.b64encode(raw).decode()
print(f'Storyboo.TTF: {len(raw)//1024} KB raw -> {len(b64)//1024} KB base64')

face = ("@font-face{font-family:'Storyboo';"
        "src:url(data:font/ttf;base64," + b64 + ") format('truetype');"
        "font-weight:normal;font-style:normal;font-display:swap}\n")

idx = os.path.join(ROOT, 'index.html')
s = io.open(idx, encoding='utf-8').read()

# 1) drop the external Poppins import (now unused, removes a network fetch)
s = re.sub(r"@import url\('https://fonts\.googleapis\.com/[^']*'\);\n?", '', s)

# 2) install the @font-face at the very top of the first <style> block
m = re.search(r'<style>', s)
assert m, '<style> not found'
s = s[:m.end()] + '\n' + face + s[m.end():]

# 3) point every Poppins reference at Storyboo (CSS + canvas font strings)
n = s.count('Poppins')
s = s.replace('Poppins', 'Storyboo')

io.open(idx, 'w', encoding='utf-8', newline='\n').write(s)
print(f'swapped {n} Poppins refs -> Storyboo; index.html now {len(s)//1024} KB')
