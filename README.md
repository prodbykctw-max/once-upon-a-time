# LUber — Listening Party Companion App

**Bespoke companion app for LAYA's "LUber" single release.**

🔗 **Live:** https://luber.app
📅 **Event:** June 20, 2026 · 8-11 PM ET · Georgia Luxury Automotive - Concord · Smyrna, GA
🎵 **Single:** [LUber](https://open.spotify.com/track/08xEJQb6PB0vxxEpdlhT0o) by LAYA

**Current production version: v1.9.0** (modular refactor shipped 2026-05-25; Worker remains v1.8.0)

---

## What this is

A custom-built release app that gives LAYA's fans a cinematic, branded experience around her single drop and listening party. What major-label artists get from agencies — built for indie artists at indie scale.

**Fan-facing features:**

- Cinematic intro with the Black SLAYA 9000 car
- RSVP to unlock the full app + secure a spot at the listening party
- In-app music player (Slide FM) embedding LUber + LAYA's Spotify catalog
- Chad GPT — AI concierge with Southern hospitality, answers questions about LAYA, the event, the song. Recognizes RSVP'd fans by name (v1.8.0).
- LTNB News broadcast hub (live stream, replays, ticker)
- Streaming destination links (Spotify, Apple Music, YouTube Music, SoundCloud)
- Push notifications via VAPID Web Push — bell button + iOS install banner for opt-in event alerts
- PWA install (Add to Home Screen) with dark-mode icon variants + 11 iOS device-specific splash screens
- Press kit + privacy disclosure
- Photo memory wall (post-event)
- RSVP backfill modal — recovers pre-v1.8 fans into Chad recognition (v1.8.0)

**Admin features:**

- Live RSVP tracker dashboard
- One-click YouTube live stream switcher
- Chad GPT analytics
- Photo gallery moderation queue
- Push subscriber tracking (PUSH SUBS card + per-RSVP 🔔/○ indicators)
- Push broadcast endpoint (admin sends notifications to all subscribers)
- Manual + auto refresh

---

## Architecture overview

```
┌─────────────────────────────────────────────────────────────┐
│                      USER (web / PWA)                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              │  HTTPS · 300+ Cloudflare POPs · HSTS enforced
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  CLOUDFLARE PAGES (luber.app)                │
│   - Static HTML shell (no-cache, ~22 KB)                     │
│   - Pre-compiled React bundle (~204 KB, content-hashed)      │
│   - Tree-shaken: only used lucide icons inlined              │
│   - Self-hosted vendor: react@18.3.1, EmailJS@4              │
│   - All scripts SHA-384 SRI-pinned                           │
│   - Service worker (sw.js) + manifest for PWA install        │
│   - 1-year immutable cache on assets                         │
│   - Auto-deploy on push to main (frontend/**)                │
└─────────────────────────────────────────────────────────────┘
                              │
                              │  POST /api/rsvp · POST /api/chad · /api/push/* · etc.
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              CLOUDFLARE WORKER (api.luber.app)               │
│   - ~22 endpoints (RSVP, dashboard, chad, gallery, stream,   │
│       push subscribe/unsubscribe/broadcast/stats, admin ops, │
│       backfill lookup)                                       │
│   - Per-IP rate limit (30/min RSVP, 30/hr Chad, 5/10min      │
│       lookup)                                                │
│   - Email dedupe via idx:email:<lc> KV index                 │
│   - Turnstile CAPTCHA validation (soft-fail mode, Bug 13)    │
│   - Anthropic Claude Haiku 4.5 LLM (Chad GPT, fan-aware)     │
│   - Constant-time admin key compare (timing-attack safe)     │
│   - Live stream config: GET public / POST admin              │
│   - Web Push: VAPID JWT (ES256) + aes128gcm encryption       │
│   - Cron handler: 3 scheduled broadcasts for June 20         │
│   - Edge cache on /api/dashboard + /api/stream-config (30s)  │
│   - Auto-deploy via GitHub Actions on push to main           │
│       (worker/**)                                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              │  R/W
                              ▼
┌──────────────────┐    ┌─────────────────────┐    ┌───────────┐
│ Cloudflare KV    │    │ Anthropic API       │    │ EmailJS   │
│ (RSVP records,   │    │ (Chad GPT LLM)      │    │ (Tx mail) │
│  counters,       │    │ name-only fan ctx   │    │ self-host │
│  gallery items,  │    │                     │    │ + SRI     │
│  stream config,  │    │                     │    │           │
│  push subs)      │    │                     │    │           │
└──────────────────┘    └─────────────────────┘    └───────────┘
```

---

## Why this architecture

### Modular React (v1.9.0)

The frontend is organized into **39 files across four layers** — `constants/`, `lib/`, `hooks/`, `components/` — with `luber_app.jsx` reduced to a ~928-line orchestration shell.

**This wasn't always the case.** From v1.0 through v1.8.0, the frontend was a single ~5,500-line component. That was a deliberate one-shot-product trade-off: fast iteration, no team coordination overhead, no onboarding cost. It served LUber well through ~20 production releases.

The refactor shipped **2026-05-25** (v1.9.0) once the codebase reached the size where:
- VS Code editor performance was degrading
- Diff readability in code review was failing
- The product was clearly going to be reskinned for other artists (KCTW Framework template)

The refactor methodology — **surface-and-pause discipline, audit ledger, ±10% bundle drift cap** — is documented in `PHASE_AUDIT.md` and is now the template for future big refactors.

**Key invariants the refactor preserved:**
- Zero new dependencies
- Zero behavior changes (one logged intent-restoring change: RSVP toast 2400→4000ms per v1.7 author intent)
- Bundle drift +1.4% (201.3 → 204.1 KB)
- 53 commits across 6 phases, each build-verified and independently revertable
- All `// v1.x.x:` history markers preserved verbatim

See `docs/ARCHITECTURE.md` for the module-by-module breakdown.

### Pre-compiled JSX + tree-shaken bundle

- **Pre-compile via esbuild** — zero in-browser Babel
- **Tree-shake lucide-react** — bundles only the icons used (currently 38 out of ~1,500 in the library)
- **External React + ReactDOM** — stay as separate vendor scripts for browser caching
- **Result:** JS payload 687 KB → ~204 KB minified, slow-3G DCL 23 sec → 16 sec

### Cloudflare Pages + Worker (both auto-deployed)

- 300+ POPs with automatic HTTP/3, Brotli, edge caching
- $0/month at our scale
- KV + Workers auth via single dashboard
- Edge functions <1ms cold-start
- Auto-deploy from GitHub: push to `main`, deploy in ~2 min (Pages) or ~30 sec (Worker)

### Defense in depth (RSVP submission)

- **Honeypot field** — invisible to humans, auto-filled by bots → silent drop
- **Cloudflare Turnstile** — invisible CAPTCHA, currently in **soft-fail mode** (logs invalid tokens but accepts the RSVP) due to Bug 13
- **Per-IP rate limit** — 30 submissions/min at Worker level
- **Email dedupe** — re-submit returns existing record, frontend shows "Welcome back" toast

Any layer can fail without blocking real users.

### Push notifications (Web Push, native)

- **VAPID JWT (ES256)** for authentication — RFC 8292
- **aes128gcm payload encryption** — RFC 8291
- Implemented natively in Worker via Web Crypto API — no external library
- Sub keys derived per-subscription with ECDH key agreement
- Bell button UI with 5 states (not-supported / unsubscribed / requesting / subscribed / denied)
- iOS Safari install banner (Apple gates push to installed PWAs only)
- Dead subscriptions (410 Gone) auto-cleaned on each broadcast
- Cron handler with 3 pre-written broadcasts for June 20 (1pm / 7:45pm / 8pm ET) — triggers wired in Cloudflare dashboard

### Chad GPT fan recognition (v1.8.0, privacy-first)

- Frontend persists RSVP record to `localStorage.luber_rsvp_user` on submit
- On reload, rehydrates from localStorage (was previously memory-only)
- `/api/chad` request body includes `rsvpUser: { full_name }` when fan is confirmed RSVP'd — **name only**, no email/phone in transit
- Worker `askChad()` parses, extracts first name (last name dropped before going to Anthropic API), injects "THIS FAN" block into Chad's system prompt
- Chad uses name occasionally for warmth, never sycophantically
- Pre-v1.8 fans recovered via backfill modal: fan enters email → `/api/rsvp/lookup?email=X` returns `full_name` only → localStorage populated

---

## Performance

| Metric                      | Value                                                 |
| --------------------------- | ----------------------------------------------------- |
| First Contentful Paint      | ~280 ms (WiFi)                                        |
| DOM Content Loaded          | ~226 ms (WiFi), ~2.0 sec (Fast 4G), ~16 sec (Slow 3G) |
| Total transfer (cold cache) | 1.5 MB                                                |
| Live CDN throughput         | 402 req/s sustained, 0 failures at 200 concurrent     |
| Bundle size (deploy zip)    | ~12 MB (mostly assets)                                |
| Compiled JS (gzipped)       | ~52 KB                                                |
| Modular bundle drift        | +1.4% from pre-refactor (well within ±10% budget)     |

### Capacity

Designed for 100,000+ concurrent users at event peak.

| Subsystem                  | Capacity                                                                       |
| -------------------------- | ------------------------------------------------------------------------------ |
| Cloudflare Pages (static)  | Effectively unlimited                                                          |
| Cloudflare Worker          | 1,000+ req/sec                                                                 |
| Cloudflare KV writes       | 1,000/sec global                                                               |
| Anthropic API (Haiku tier) | ~1,000 RPM, protected by 99 canned-response patterns absorbing ~75% of queries |

---

## Routes

- `/` — main trip card (countdown, streaming destinations, RSVP)
- `/?view=press` — press kit / EPK
- `/?view=privacy` — privacy + AI disclosure
- `/?view=dashboard` — admin dashboard (password-gated via `ADMIN_KEY` Worker secret)
- `/?view=live` — LTNB News live broadcast page
- `/?view=gallery` — photo memory wall (post-event)
- `/?view=merch` — merch shop (when activated)
- `/?dev=1` — bypass tap-to-enter + RSVP gate (development/admin only)
- `?phase=pre|live|post` — manual event phase override (testing)

---

## Event phases

| Phase    | Window (Eastern Time)                    | Behavior                            |
| -------- | ---------------------------------------- | ----------------------------------- |
| **PRE**  | until June 20, 2026 5:59 PM ET           | Countdown + RSVP active             |
| **LIVE** | June 20 6:00 PM ET → June 21 midnight ET | Broadcast view, LTNB News goes live |
| **POST** | June 21 onward                           | Memory wall opens                   |

---

## Build pipeline

Source: `frontend/src/` (modular tree under `constants/`, `lib/`, `hooks/`, `components/`). Build script: `frontend/build_treeshake.js`.

```powershell
cd frontend
npm install
node build_treeshake.js
# Output: out/vendor/app.compiled.treeshake.{hash}.min.js + updated out/index.html with new SRI hash
```

`build_treeshake.js` includes auto SHA-256 content hash (8-char suffix), SHA-384 SRI hash for browser integrity check, and `out/index.html` rewrite in-place + cleanup of stale bundles.

---

## Deploy

### Frontend (Cloudflare Pages, auto-deploy)

Push to `main` touching `frontend/**` → Cloudflare Pages auto-builds and deploys to luber.app in ~2 min. No manual upload needed.

### Worker (Cloudflare Workers, auto-deploy via GitHub Actions)

Push to `main` touching `worker/**` → `.github/workflows/deploy-worker.yml` triggers, runs `wrangler deploy` on ephemeral Ubuntu container in ~30 sec.

Worker secrets are configured via Cloudflare dashboard (all 6 are encrypted Secret type, survives deploys):

| Variable            | Type   | Purpose                |
| ------------------- | ------ | ---------------------- |
| `ANTHROPIC_API_KEY` | Secret | Chad GPT               |
| `ADMIN_KEY`         | Secret | Dashboard auth         |
| `TURNSTILE_SECRET`  | Secret | CAPTCHA validation     |
| `VAPID_PRIVATE_KEY` | Secret | Web Push signing       |
| `VAPID_PUBLIC_KEY`  | Secret | Web Push public key    |
| `VAPID_SUBJECT`     | Secret | Web Push subject claim |

Verify: `https://api.luber.app/api/health` should return `version: "v1.8.0"` and all configured flags `_configured: true`.

---

## Security & resilience

- **HSTS** enforced at edge (`max-age=31536000; includeSubDomains`)
- **HTTPS** forced via Cloudflare "Always Use HTTPS"
- **Subresource Integrity (SRI)** SHA-384 hashes on all 4 self-hosted vendor scripts
- **Self-hosted dependencies** (no CDN failure risk, no supply-chain attacks)
- **Constant-time admin key compare** in Worker (timing-attack resistant)
- **Per-IP rate limiting** on RSVP + Chad + lookup endpoints
- **Honeypot field** + Cloudflare Turnstile (soft-fail mode)
- **React ErrorBoundary** with branded fallback for graceful failure
- **Chad GPT degradation** → falls back to client-side regex matcher (99 patterns) if Anthropic API errors
- **Strict CORS** on Worker (only allowlisted origins)
- **No PII in localStorage** beyond what fan typed (full_name + email + phone), explicit to the fan
- **Content-hashed JS filenames** → cache busting works automatically per build
- **HTML no-cache** → PWA always picks up latest hash on relaunch
- **`<noscript>` fallback** → event info + DSP links visible even with JS disabled
- **Web Push cryptography** — VAPID JWT (ES256, P-256) + aes128gcm payload encryption (RFC 8291), implemented natively via Web Crypto API in Worker
- **Push subscription cleanup** — 404/410 responses auto-prune dead subscriptions from KV index
- **Supply chain hygiene** — no local `npm install`, all dependency resolution on ephemeral runners

---

## Built by

**KCTW** ([@prodbykctw](https://instagram.com/prodbykctw)) for **LAYA** ([@layaface](https://instagram.com/layaface))
In association with **BASILICA** ([@highbasilica](https://instagram.com/highbasilica))

PRODBYKCTW LLC · © 2026 LAYA
