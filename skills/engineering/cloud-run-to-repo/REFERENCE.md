# Reference

## Build approach: buildpack vs Dockerfile+uv

Source-deployed Cloud Run services build with **Google Cloud buildpacks**, which install from
`requirements.txt` (pip) — they do **not** run `uv`. So "use uv" and "keep source deploy" partly
conflict. Two clean resolutions — present both, recommend (A) for small/internal services:

**(A) Buildpack + uv-for-dev (default, KISS).** Keep `gcloud run deploy --source .`. Manage deps with
uv locally; commit a generated `requirements.txt` for the buildpack. Keeps the buildpack's **automatic
base-image security updates** and, for functions, its implicit `functions-framework` wiring. Cost: a
generated file to keep in sync (handled by regenerating it in `deploy.sh`).

**(B) Dockerfile + uv.** A ~10-line Dockerfile using `uv sync`/`uv run` (`gcloud run deploy --source .`
auto-detects the Dockerfile). uv drives the build; one lockfile as truth; no `requirements.txt`. Cost:
you own the Dockerfile, the `functions-framework` run command, and **base-image patching** (you lose
automatic updates). Worth an ADR — it's a surprising, semi-reversible trade-off.

Rule of thumb: tiny internal cron/function → (A). Larger app where uv purity and reproducibility matter,
or where you already own a Dockerfile → (B).

## Config mapping: describe output → deploy.sh flags

`recover-source.sh` prints these. Map them:

| From the service | deploy.sh flag |
|---|---|
| `serviceAccountName` | `--service-account` |
| `resources.limits.cpu` / `.memory` | `--cpu` / `--memory` |
| `containerConcurrency` | `--concurrency` |
| `timeoutSeconds` | `--timeout` |
| `maxScale` annotation | `--max-instances` |
| `startup-cpu-boost: true` annotation | `--cpu-boost` |
| `ingress` annotation | `--ingress` (omit if `all`) |
| `invoker-iam-disabled: 'true'` | `--allow-unauthenticated` (else `--no-allow-unauthenticated`) |
| `build-function-target` (non-empty) | `--function <target>` |
| non-secret `env` entries | `--set-env-vars K=V,...` |
| secrets | `--set-secrets K=secretname:latest` (Secret Manager) |

Gotchas learned the hard way:
- The gcloud flag is `--function`, **not** `--function-target` (that's only the annotation name).
- `invoker-iam-disabled: 'true'` is how "allow unauthenticated" shows up in `describe`.
- If `gcloud run deploy --help` is blocked by a permission rule, confirm flag names from the SDK source:
  `grep -rn "'--flag'" $(gcloud info --format='value(installation.sdk_root)')/lib/googlecloudsdk/command_lib/run/flags.py`.
- A uv-exported `requirements.txt` is fully pinned (all transitives) — more reproducible, but the **first**
  redeploy differs from the previously floating buildpack build. Tell the user so they watch that revision.

## deploy.sh template

```bash
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

PROJECT="..."; SERVICE="..."; REGION="..."
SERVICE_ACCOUNT="..."

echo ">> Regenerating requirements.txt from uv.lock"
uv export --no-hashes --no-emit-project --no-dev --format requirements-txt -o requirements.txt

gcloud run deploy "${SERVICE}" \
  --source . --project "${PROJECT}" --region "${REGION}" \
  --function main \                     # omit if not a Functions Framework app
  --service-account "${SERVICE_ACCOUNT}" \
  --allow-unauthenticated \             # match invoker-iam-disabled
  --memory 8Gi --cpu 2 --concurrency 80 --timeout 300 --max-instances 100 --cpu-boost \
  --set-env-vars "KEY=value,..."        # secrets go through --set-secrets instead
```

Keep every runtime flag explicit: `gcloud run deploy` on an existing service leaves unspecified
settings as-is, but making them explicit means the repo is the source of truth and a fresh recreate
is faithful.

## Image-extraction fallback (no source tarball)

When `recover-source.sh` reports no `build-source-location`, the service runs a prebuilt image. Recover
the app from the image (best-effort — this is a container, not clean source):

```bash
IMAGE="$(gcloud run services describe SERVICE --region REGION \
  --format="value(spec.template.spec.containers[0].image)")"
docker create --name _crun "$IMAGE"
docker cp _crun:/app ./recovered-app     # /app is the usual buildpack workdir; try /workspace too
docker rm _crun
```
Then inspect the image's entrypoint/cmd (`docker inspect "$IMAGE"`) for the run command, and treat the
result as a starting point to rebuild a clean repo rather than authoritative source.
