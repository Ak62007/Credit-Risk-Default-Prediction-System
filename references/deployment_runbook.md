# Deployment Runbook

This system is deployed as a live, on-demand demo on a single AWS EC2 instance — spun up before a demo/interview and stopped afterward, not run always-on. This keeps AWS costs near zero between uses. This runbook is intentionally separate from the main 23-milestone project plan: it documents *operating* the already-built system, not building it.

**Public-facing address:** `http://13.62.186.62/` (Basic Auth protected — credentials known to the project owner, not documented here since this repo is public)

**Architecture:** one EC2 instance (`t3.small`, Elastic IP `13.62.186.62`) running nginx as a reverse proxy in front of three services:

| Path | Service | Port | How it runs |
|---|---|---|---|
| `/` | Dashboard frontend (Next.js) | 3000 | Native `node server.js`, manually started in tmux |
| `/dashboard-api/` | Dashboard backend (FastAPI) | 8001 | Native `uv run uvicorn`, manually started in tmux |
| `/api/` | `/predict` inference API | 8000 | Docker container, auto-restarts with the instance |

MLflow (port 5000) is **not** part of the live demo — it's only needed when rebuilding the Docker image with a new model version. Leaving it stopped during normal demo use saves real memory on this instance (see gotchas below).

## Starting the demo

1. **Start the EC2 instance.** AWS Console → EC2 → Instances → `mlflow-tracking-server` (`i-065e87a456e557f9b`) → Instance state → Start instance.
   - If you hit `InsufficientInstanceCapacity`, this is a transient AWS-side issue — just retry after a minute.
   - The Elastic IP (`13.62.186.62`) stays the same across every start/stop, so nothing else needs updating.

2. **SSH in and start tmux** (a fresh session every time — tmux sessions don't survive a stop/start, only a plain reboot):
   ```bash
   ssh -i /Users/ak007/.ssh/ec2-connection-key-pair.pem ec2-user@13.62.186.62
   tmux new -s deploy
   ```

3. **Check the `/predict` API container is already running** — it should auto-restart on its own (`--restart unless-stopped`), no manual step needed:
   ```bash
   docker ps
   ```
   If it's not listed, start it manually:
   ```bash
   docker start credit-risk-api
   ```

4. **Check nginx is running** — also auto-starts via systemd, no manual step needed:
   ```bash
   sudo systemctl status nginx
   ```
   If it's not active: `sudo systemctl start nginx`

5. **Start the dashboard backend** (new tmux window, `Ctrl+b c`):
   ```bash
   cd ~/Credit-Risk-Default-Prediction-System/dashboard/backend
   uv run uvicorn app.main:app --host 127.0.0.1 --port 8001
   ```

6. **Start the dashboard frontend** (new tmux window, `Ctrl+b c`):
   ```bash
   cd ~/Credit-Risk-Default-Prediction-System/dashboard/frontend/standalone
   HOSTNAME=127.0.0.1 PORT=3000 node server.js
   ```

7. **Verify, from your own machine (not SSH'd in):**
   ```bash
   curl -u ak0007 -I http://13.62.186.62/                                    # frontend
   curl -u ak0007 http://13.62.186.62/dashboard-api/api/health               # dashboard backend
   curl -u ak0007 -I http://13.62.186.62/api/docs                            # predict API
   ```
   All three should return `200 OK` / healthy JSON. Then open `http://13.62.186.62/` in a browser and click through Overview, Drift Monitoring, Predictions, and Data Health.

## Stopping the demo

1. (Optional tidiness) `Ctrl+C` the dashboard backend and frontend in their tmux windows.
2. **Stop the EC2 instance** — the important step, this is what actually stops billing: AWS Console → EC2 → Instances → Instance state → Stop instance.

That's it — the Docker container, nginx config, and everything on disk persists across a stop; only running (non-Docker) processes are lost.

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

## Rebuilding the `/predict` API image (only when the model changes)

This needs MLflow running temporarily. See the full known-good startup command and reasoning in project memory / `data_card.md`'s M16 section. Outline: start MLflow (with the job-execution env var set) in its own tmux window → `set -a; source .env; set +a` → `docker build --network=host --secret ...` → stop MLflow again once the build succeeds and CI (if pushed to `main`) passes.
