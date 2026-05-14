## What this folder is

`example/` is a small TypeScript codebase used as **input** to the **Codebase Almanac** skill (`Skill48414`). It exists so you can try the almanac without pointing it at one of your own projects.

It is *not* meant to be installed, run, or deployed. It's reading material for a static analyzer.

## Two ways to use it

**1. Generate the almanac yourself.** In Cursor:

```text
Run the codebase almanac on example/
```

Or in Claude Code:

```text
/codebase-almanac
Run it on example/
```

The skill will produce a single `.html` file with Overview / Product / Technical / Security / Pitch / Simulation tabs and open it in your browser.

**2. Open the prebuilt almanac.** Open `example/visualization.html` directly — same output, no skill run needed.

## What the codebase represents

A toy expense-tracker API ("SpendWise") written as a tiny npm workspace:

- `packages/shared/` — a few input-validation helpers shared with any client
- `packages/api/` — an Express + better-sqlite3 service with JWT auth, helmet, CORS, rate limiting, and a `/api/auth` route group

It is deliberately scoped down to one route group. The almanac doesn't need a large codebase to produce a useful map; this size keeps the generated HTML readable.

## About the security findings

The Security tab will flag several issues — that's the point. The code intentionally contains realistic antipatterns so the almanac has something to surface:

- JWT secret falls back to a hardcoded string when `JWT_SECRET` is unset (`middleware/authenticate.ts`, `controllers/authService.ts`)
- CORS falls back to a wildcard `*` origin when `ALLOWED_ORIGINS` is unset (`server.ts`)
- The in-memory rate limiter trusts `req.ip` with no `app.set('trust proxy')` (`middleware/rateLimiter.ts`)
- Non-production responses echo raw `err.message` (`middleware/errorHandler.ts`)

**Do not copy this code into a real project.** Treat it the way you would a "spot the bug" exercise — useful for showing what the almanac detects, harmful if shipped.
