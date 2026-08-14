#!/usr/bin/env python3
"""AutoSprite MCP-over-HTTP client.

Why this exists: claude.ai's AutoSprite connector authenticates with OAuth, so it
only works from a browser session. AutoSprite's own MCP endpoint wants a plain
`Authorization: Bearer <key>`. Every cloud session that needed art has had to
re-derive this by hand; now it lives here.

    ENDPOINT   POST https://www.autosprite.io/api/mcp
    TRANSPORT  JSON-RPC 2.0, responses come back as SSE (`event:`/`data:` lines)
    AUTH       Authorization: Bearer $AUTOSPRITE_KEY   (key page: /apikey)

The key is read from the environment ONLY. Never write it to a file, never pass
it on a command line (it lands in shell history and `ps`), never commit it.

    export AUTOSPRITE_KEY=vspk_...
    python3 tools/autosprite.py tools                       # list tool schemas
    python3 tools/autosprite.py call list_characters '{"limit":5}'
    python3 tools/autosprite.py ping                         # transport check, no key needed

Exit codes: 0 ok · 1 tool returned isError · 2 transport/JSON-RPC error · 3 no key.
"""
import json
import os
import sys
import urllib.request

URL = 'https://www.autosprite.io/api/mcp'
PROTOCOL = '2024-11-05'


def rpc(method, params=None, key=None, timeout=180):
    """One JSON-RPC call. Returns the parsed `result`, raises RuntimeError on `error`."""
    body = json.dumps({
        'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': params or {},
    }).encode()
    headers = {
        'Content-Type': 'application/json',
        # The server replies with SSE regardless; it still requires the offer.
        'Accept': 'application/json, text/event-stream',
    }
    if key:
        headers['Authorization'] = 'Bearer ' + key
    req = urllib.request.Request(URL, data=body, headers=headers, method='POST')
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode('utf-8', 'replace')

    # SSE framing: the payload is on `data:` lines. Take the last complete one.
    payload = None
    for line in raw.splitlines():
        if line.startswith('data:'):
            payload = line[5:].strip()
    if payload is None:
        payload = raw.strip()
    msg = json.loads(payload)
    if 'error' in msg:
        raise RuntimeError(json.dumps(msg['error']))
    return msg.get('result', {})


def call(name, arguments, key):
    """tools/call, unwrapping the content envelope. Returns (text, is_error)."""
    res = rpc('tools/call', {'name': name, 'arguments': arguments}, key=key)
    text = '\n'.join(
        c.get('text', '') for c in res.get('content', []) if c.get('type') == 'text'
    )
    return text, bool(res.get('isError'))


def main(argv):
    cmd = argv[1] if len(argv) > 1 else 'ping'
    key = os.environ.get('AUTOSPRITE_KEY') or os.environ.get('AUTOSPRITE_API_KEY')

    # `initialize` and `tools/list` are open; only tools/call needs the key.
    if cmd == 'ping':
        info = rpc('initialize', {
            'protocolVersion': PROTOCOL, 'capabilities': {},
            'clientInfo': {'name': 'jande-cli', 'version': '1'},
        })
        print(json.dumps(info.get('serverInfo', {}), indent=2))
        print('key in environment:', 'yes' if key else 'NO')
        return 0

    if cmd == 'tools':
        for t in rpc('tools/list').get('tools', []):
            print('%-22s %s' % (t['name'], t.get('description', '').split('\n')[0]))
        return 0

    if cmd == 'call':
        if not key:
            print('AUTOSPRITE_KEY is not set. Get one at '
                  'https://www.autosprite.io/apikey and export it — do not '
                  'write it to a file.', file=sys.stderr)
            return 3
        name = argv[2]
        args = json.loads(argv[3]) if len(argv) > 3 else {}
        text, err = call(name, args, key)
        print(text)
        return 1 if err else 0

    print(__doc__, file=sys.stderr)
    return 2


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv))
    except Exception as e:  # transport, HTTP, or JSON-RPC level
        print('%s: %s' % (type(e).__name__, e), file=sys.stderr)
        sys.exit(2)
