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

## The game's URL is fixed

`LB_URL` in `index.html` is hard-coded to the deployed Worker. There is
deliberately **no** `?lb=` or localStorage override any more: that override
persisted an attacker-supplied URL and fed its rows into the page (stored XSS,
security audit 2026-10-06). Changing the Worker URL means editing `LB_URL`.

## Security (2026-10-06)

- CORS is granted only to `https://prodbykctw-max.github.io`; `POST /submit`
  from any other Origin (or none) gets 403.
- `SUBMIT_LIMIT` (Workers Rate Limiting, namespace 3001): 5 submits / 60 s per
  `CF-Connecting-IP`. Skipped if the binding is absent.
- Plausibility caps (derived from the game code, see the constants in
  `leaderboard-worker.js`): `dur` (run seconds) is required; runner distance
  <= 40 m/s and score <= 5,000/m + 100k; RPG stage distance <= 600 and score
  <= 30,000/s + 100k (15M absolute). Rejected runs get a generic 400.
- Errors return a generic 500 (no exception text).
- Tests: `node --test cloudflare/leaderboard-worker.test.mjs`.
- Deploy order: publish the game (it sends `dur`) BEFORE the Worker, or
  submissions from the old page are rejected until it updates.

## Test the API directly

```bash
BASE=https://jande-leaderboard.<your-subdomain>.workers.dev
curl -s "$BASE/top?mode=all&n=10"
```

## Endpoints

- `GET /top?mode=all|side|temple&n=20` → `{ ok, mode, runs:[{n,d,s,m,t}] }`
- `POST /submit` `{ name, dist, score, mode, dur }` → `{ ok, rank }`
- `POST /registry` `{ name?, email }` → `{ ok }` — Queen's Registry sign-up. Same
  Origin rule as `/submit` (403 otherwise). Stored in the same KV under
  `registry:<lowercased email>` (a repeat sign-up overwrites). Stores name, email
  and a server timestamp only — no IP, no location. Body capped at 2 KB.
- `GET /registry/export` → `{ ok, count, signups:[{name,email,time}] }`. Returns
  404 (same as an unknown route) unless the request has
  `Authorization: Bearer <REGISTRY_EXPORT_KEY>`.

Runs are sorted by distance then score, deduped to each name's best, capped at 100.

## Registry export key (one-time, owner)

```bash
cd cloudflare
npx wrangler secret put REGISTRY_EXPORT_KEY   # paste a long random string
npx wrangler deploy
# export the list:
curl -s -H "Authorization: Bearer <that string>" https://jande-leaderboard.prodbykctw.workers.dev/registry/export
```

Until the secret is set, `/registry/export` is a 404 for everyone. Sign-ups are
still being saved. Deploy order: the Worker first (so `POST /registry` exists),
then the game page.
