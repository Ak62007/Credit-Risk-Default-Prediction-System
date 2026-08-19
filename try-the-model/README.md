# try-the-model

A small, public-facing demo app for the credit risk default prediction project. Visitors fill out a
simplified loan application and get a live prediction from the real deployed model — no login, no
mockup data.

This is separate from `dashboard/`, which is a Basic-Auth-gated operator monitoring dashboard. This
app is the opposite: unauthenticated, single-purpose, and meant to be shared with anyone.

## How it works

- `credit_risk/api/schemas.py`'s `RequestModel` has ~65 fields. This app exposes only the ~13 most
  meaningful ones as real form inputs (loan amount, income, DTI, FICO, etc.) and derives the rest
  deterministically and consistently in `lib/buildPayload.ts`, so a full submitted payload is
  realistic even though the visitor only ever touches a handful of sliders.
- Three example profiles (`lib/presets.ts`) — typical / low-risk / high-risk — can be loaded and then
  tweaked.
- The browser never talks to the real `/predict` API directly. `app/api/predict/route.ts` is a
  server-side proxy: it forwards the built payload to `PREDICT_API_URL` and returns the response.
  This avoids CORS (the real API has none configured, and is treated as a stable external contract
  this app doesn't modify) and keeps the API URL out of client-side code.
- The response's SHAP `reason_codes` are translated into plain-language sentences in
  `lib/explainReasonCodes.ts` instead of showing raw feature names/values.

## Running locally

1. Make sure the real API is running (from the repo root):
   ```
   uv run uvicorn credit_risk.api.main:app --reload
   ```
   (defaults to `http://127.0.0.1:8000`)

2. In this directory:
   ```
   cp .env.local.example .env.local   # adjust PREDICT_API_URL if needed
   npm install
   npm run dev
   ```
   Then open http://localhost:3000.

Deployment (e.g. to EC2) is a separate step, not covered here.
