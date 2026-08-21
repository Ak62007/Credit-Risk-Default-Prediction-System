# Deployment Runbook

This system is deployed as a live, on-demand demo on a single AWS EC2 instance — spun up before a demo/interview and stopped afterward, not run always-on. This keeps AWS costs near zero between uses. This runbook is intentionally separate from the main 23-milestone project plan: it documents *operating* the already-built system, not building it.

**Public-facing address:** `https://credit-risk.adii.codes/` — fully public, no login required. Basic Auth originally gated the dashboard, but was deliberately removed (2026-08-21) so recruiters/interviewers can reach it with just a link: nothing behind it is sensitive (synthetic prediction logs + the public LendingClub dataset), and ease of access matters more than gating a portfolio piece. `https://credit-risk.adii.codes/try-the-model/` is the separate public inference demo, also no login required.

**Architecture:** one EC2 instance (`t3.small`, Elastic IP `13.62.186.62`, DNS A record `credit-risk.adii.codes` → this IP) running nginx as a TLS-terminating reverse proxy in front of four services:

| Path | Service | Port | How it runs |
|---|---|---|---|
| `/` | Dashboard frontend (Next.js) | 3000 | systemd service `dashboard-frontend`, auto-starts on boot |
| `/dashboard-api/` | Dashboard backend (FastAPI) | 8001 | systemd service `dashboard-backend`, auto-starts on boot |
| `/api/` | `/predict` inference API | 8000 | Docker container, auto-restarts with the instance |
| `/try-the-model/` | Public inference demo (Next.js) | 3001 | systemd service `try-the-model`, auto-starts on boot |

As of 2026-08-21, **all four services plus nginx auto-start with the instance — no manual startup steps needed at all.** This is a change from earlier in the project, when the three native services had to be started by hand in tmux every time. See "Systemd services" below for how these are managed now.

MLflow (port 5000) is **not** part of the live demo — it's only needed when rebuilding the Docker image with a new model version. Leaving it stopped during normal demo use saves real memory on this instance (see gotchas below).

## Starting the demo

1. **Start the EC2 instance.** AWS Console → EC2 → Instances → `mlflow-tracking-server` (`i-065e87a456e557f9b`) → Instance state → Start instance.
   - If you hit `InsufficientInstanceCapacity`, this is a transient AWS-side issue — just retry after a minute.
   - The Elastic IP (`13.62.186.62`) and the domain (`credit-risk.adii.codes`) stay the same across every start/stop, so nothing else needs updating.
2. **Wait ~30-60 seconds** for the instance to finish booting — nginx, the `/predict` Docker container, and all three native services come up automatically via systemd, no SSH session required.
3. **Verify, from your own machine:**
   ```bash
   curl -I https://credit-risk.adii.codes/                          # dashboard frontend (expect 200, no auth)
   curl https://credit-risk.adii.codes/dashboard-api/api/health     # dashboard backend
   curl -I https://credit-risk.adii.codes/api/docs                 # predict API docs
   curl -I https://credit-risk.adii.codes/try-the-model/            # public demo (expect 200, no auth)
   ```
   Then open `https://credit-risk.adii.codes/` in a browser and click through Overview, Drift Monitoring, Predictions, and Data Health, and separately check `https://credit-risk.adii.codes/try-the-model/`.

If anything doesn't come up on its own, SSH in and check the relevant systemd service (see below) before assuming something's broken.

## Stopping the demo

1. **Stop the EC2 instance** — AWS Console → EC2 → Instances → Instance state → Stop instance. This is the only step; nothing needs manual cleanup first, since all services are systemd-managed and will simply be stopped along with the instance and restarted automatically next time.

That's it — the Docker container, nginx config, TLS certificate, and everything on disk persists across a stop; only running processes are lost, and those all come back on their own.

## Systemd services

The three native services are managed as systemd units at `/etc/systemd/system/{dashboard-backend,dashboard-frontend,try-the-model}.service`. Useful commands:

```bash
sudo systemctl status <service-name>      # check if it's running, see recent log lines
sudo journalctl -u <service-name> -n 50   # see more log history
sudo systemctl restart <service-name>     # restart after a config change
```

**Redeploying a new build** (e.g. after a code change to the dashboard frontend or `try-the-model`): build locally on your Mac (same as before — `npm run build`, copy `public`/`.next/static` into the standalone output, `tar -czf` into one archive), `scp` the archive to the EC2 box, then:

```bash
sudo systemctl stop <service-name>
rm -rf <path-to-standalone-dir>/*
tar -xzf ~/<archive-name>.tar.gz -C <path-to-standalone-dir>
sudo systemctl start <service-name>
```

`dashboard-backend` doesn't need a rebuild step for code changes since it runs directly from the repo via `uv run` — just `git pull` in the repo directory, then `sudo systemctl restart dashboard-backend`.

## Domain and HTTPS

Domain `adii.codes` registered via name.com (free for 1 year via GitHub Student Developer Pack), with a subdomain `credit-risk.adii.codes` (A record → `13.62.186.62`) used for this project specifically — chosen so future projects can each get their own subdomain off the same root domain rather than buying a new domain per project.

TLS via Certbot (`sudo dnf install -y certbot python3-certbot-nginx` on Amazon Linux 2023 — available directly in the OS repos since late 2023, no need for a pip/virtualenv install), run as `sudo certbot --nginx -d credit-risk.adii.codes`. Certbot automatically edited `/etc/nginx/conf.d/demo.conf` to add the HTTPS server block and an HTTP→HTTPS redirect.

**Certificate expires 2026-11-19** (90-day Let's Encrypt lifetime). A systemd timer (`certbot-renew.timer`, enabled 2026-08-21) checks twice daily and auto-renews when within 30 days of expiry — but this only fires if the instance happens to be running at trigger time, which given the on/off usage model isn't guaranteed. **Practical plan:** don't rely on the timer alone — run `sudo certbot renew` manually (safe no-op if not due yet) before any demo/interview once getting close to the expiry date.

## Known gotchas quick-reference

| Symptom | Cause | Fix |
|---|---|---|
| MLflow CPU pins near 100%, SSH becomes unreachable | MLflow 3.x auto-starts a background job-execution subsystem whenever a DB backend is configured | `export MLFLOW_SERVER_ENABLE_JOB_EXECUTION=false` before starting MLflow (only relevant when rebuilding the model image) |
| `docker build` hangs indefinitely on the MLflow fetch step | Container on Docker's default bridge network can't reliably loop back to the host's own public IP (hairpin NAT) | `docker build --network=host ...` |
| Dashboard backend gets OOM-killed on startup | Full `training_set.parquet` (466k rows, ~839MB in memory) is too much for the 2GB instance once feature-engineering runs | Reference loader (`dashboard/backend/app/deps.py`) uses a 40k-row sample (`training_reference_sample.parquet`) instead |
| Dashboard loads with zero CSS styling | Next.js `standalone` build output doesn't include `public/` or `.next/static` automatically | `cp -r public .next/standalone/public` and `cp -r .next/static .next/standalone/.next/static` before packaging, every time you rebuild the frontend |
| `/api/overview` and `/api/scores/distribution` return 500 | Both read `models/tuned_xgb/metrics.json` directly off disk; that file only exists inside the Docker image (fetched at build time), not on the host running the native dashboard backend | `docker cp credit-risk-api:/app/models/tuned_xgb/metrics.json ~/Credit-Risk-Default-Prediction-System/models/tuned_xgb/metrics.json` |
| `scp`-ing many small files (e.g. `.next/standalone`) is extremely slow | Per-file SSH overhead multiplied by thousands of files, worsened by real latency to `eu-north-1` | `tar -czf` into one archive locally, `scp` the single file, `tar -xzf` on the other end |
| New SSH connection hangs for 30-60s before showing a prompt | Normal — many SSH servers do a reverse-DNS lookup on connect, unrelated to the instance's health | Just wait it out |
| Status checks all pass but SSH is completely unreachable | Instance is alive but a stuck process (e.g. runaway CPU) is starving `sshd` | A plain reboot is safe: EC2 Console → Instance state → Reboot |
| systemd service fails with "could not be found" or fails to start | `~` in a path (e.g. from `which uv`) is only expanded by interactive shells, not by systemd unit files | Use the full absolute path (e.g. `/home/ec2-user/.local/bin/uv`) in `ExecStart`/`WorkingDirectory` |
| Starting a systemd service fails because the port's already in use | A manually-started tmux process from before the systemd migration is still bound to the same port | Stop the manual process (`Ctrl+C` in its tmux window) before `systemctl start`-ing the equivalent service |
| `try-the-model` gets stuck in an infinite redirect loop (`308` ↔ `301`) | Next.js's `basePath` defaults to no-trailing-slash as canonical, while nginx's `location /try-the-model/` block redirects the no-slash form to add one — the two disagree on the canonical URL and bounce forever | Add `trailingSlash: true` to `try-the-model/next.config.ts` so Next.js's canonical form matches what nginx already redirects toward |
| Dashboard panels show "Failed to fetch" only after adding HTTPS, with a "Mixed Content" browser console error | Dashboard frontend's `NEXT_PUBLIC_API_BASE_URL` is a build-time-baked value (Next.js inlines `NEXT_PUBLIC_*` vars into the compiled JS); it was built pointing at the old plain-`http://` IP address, and HTTPS pages block active mixed-content requests to `http://` | Rebuild with `NEXT_PUBLIC_API_BASE_URL=https://credit-risk.adii.codes/dashboard-api npm run build`, redeploy |
| Dashboard sidebar squeezes the whole page into a single narrow column on mobile | `Sidebar.tsx` used a fixed `w-60` width with no responsive breakpoints, so it kept its full desktop width even on narrow phone screens | Made the sidebar responsive: hidden behind a hamburger/drawer on mobile, unchanged fixed sidebar on desktop |

## Rebuilding the `/predict` API image (only when the model changes)

This needs MLflow running temporarily. See the full known-good startup command and reasoning in project memory / `data_card.md`'s M16 section. Outline: start MLflow (with the job-execution env var set) in its own tmux window → `set -a; source .env; set +a` → `docker build --network=host --secret ...` → stop MLflow again once the build succeeds and CI (if pushed to `main`) passes.
