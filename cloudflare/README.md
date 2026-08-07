# Global leaderboard — deploy (one command)

The game already talks to this API (with a graceful fallback to the local
top‑10 when it's unreachable). It just needs the Worker deployed. The KV
namespace **`jande-leaderboard`** (`id 9dc38fa2efba4f8d9cd412b512d3c3ef`) is
already created in the Cloudflare account and wired in `wrangler.toml`.

> Why this step is manual: the cloud session can create Cloudflare KV but has
> no Worker‑deploy access (no wrangler/credentials in its sandbox, and the CF
> API is blocked by its egress policy). Deploy from the laptop session, which
> has Cloudflare access.

## Deploy

```bash
cd cloudflare
npx wrangler login          # once, opens the browser
npx wrangler deploy         # deploys leaderboard-worker.js + binds the KV
```

`wrangler deploy` prints the live URL, e.g.
`https://jande-leaderboard.<your-subdomain>.workers.dev`.

## Point the game at it (no game redeploy needed)

Open the game once with the URL as a query param — it saves to localStorage:

```
https://prodbykctw-max.github.io/once-upon-a-time/?lb=https://jande-leaderboard.<your-subdomain>.workers.dev
```

Or hand the URL to the cloud session and it'll bake it in as the default
(`LB_URL` in `index.html`) so every visitor gets it automatically.

## Test the API directly

```bash
BASE=https://jande-leaderboard.<your-subdomain>.workers.dev
curl -s "$BASE/top?mode=all&n=10"
curl -s -X POST "$BASE/submit" -H 'Content-Type: application/json' \
  -d '{"name":"TEST","dist":420,"score":9001,"mode":"side"}'
```

## Endpoints

- `GET /top?mode=all|side|temple&n=20` → `{ ok, mode, runs:[{n,d,s,m,t}] }`
- `POST /submit` `{ name, dist, score, mode }` → `{ ok, rank }`

Runs are sorted by distance then score, deduped to each name's best, capped at 100.
