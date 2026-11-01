#!/usr/bin/env python3
"""Build the GAME I OVERHAUL PREVIEW (BASILICA Production Bible 2.5) as its own file.

WHY THIS EXISTS. The overhaul replaces Jandé with Princess, retires the Groom and
re-cuts nine stages into eleven chapters. The client and Frédéric have to play it
before it goes anywhere near the public game, so it publishes ONE FOLDER DOWN at
/overhaul/ and shares the already-published web/ assets. The public game at the
root is untouched.

Source of truth: index.html on the overhaul branch. Output: overhaul/index.html
(git-ignored build artifact). Publish by adding ONLY overhaul/index.html (plus any
new web/ assets) on top of the current gh-pages tree — never an orphan rebuild
from this branch, which would replace the public game with the preview.
"""
import io, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, '..'))
SRC = os.path.join(REPO, 'index.html')
OUTD = os.path.join(REPO, 'overhaul')
OUT = os.path.join(OUTD, 'index.html')


def main():
    s = io.open(SRC, encoding='utf-8').read()

    def sub(old, new, label):
        nonlocal s
        if s.count(old) != 1:
            print('  FAIL %s: anchor matched %d times' % (label, s.count(old)), file=sys.stderr)
            sys.exit(1)
        s = s.replace(old, new)
        print('  ok   ' + label)

    # a preview is not a second public game: no indexing, no canonical claim
    sub('<link rel="canonical" href="https://prodbykctw-max.github.io/once-upon-a-time/">',
        '<meta name="robots" content="noindex,nofollow">', 'noindex instead of canonical')
    s = re.sub(r'<meta name="robots" content="(?!noindex)[^"]*">', '', s)
    sub('<title>JANDÉ — Once Upon A Time</title>', '<title>Once Upon a Time — Game I preview</title>', 'title')

    # one folder down: share the published asset folder
    before = len(re.findall(r'(?<![./\w])web/', s))
    s = re.sub(r'(?<![./\w])web/', '../web/', s)
    after = len(re.findall(r'\.\./web/', s))
    if before != after or before == 0:
        print('  FAIL asset rewrite: %d -> %d' % (before, after), file=sys.stderr)
        sys.exit(1)
    print('  ok   asset paths rewritten to ../web/ (%d refs)' % after)
    for f in ['apple-touch-icon.png', 'icon-192.png', 'icon-512.png', 'manifest.webmanifest']:
        s = s.replace('"%s"' % f, '"../%s"' % f)
    print('  ok   root icons/manifest pointed at ../')

    # every referenced asset must exist on disk (the preview 404s otherwise)
    missing = sorted(set(m for m in re.findall(r'\.\./web/([\w.]+)', s) if not os.path.exists(os.path.join(REPO, 'web', m))))
    if missing:
        print('  FAIL missing assets: ' + ', '.join(missing), file=sys.stderr)
        sys.exit(1)
    print('  ok   all referenced assets present')

    os.makedirs(OUTD, exist_ok=True)
    io.open(OUT, 'w', encoding='utf-8').write(s)
    print('-> overhaul/index.html (%.0f KB)' % (len(s.encode()) / 1024))


if __name__ == '__main__':
    main()
