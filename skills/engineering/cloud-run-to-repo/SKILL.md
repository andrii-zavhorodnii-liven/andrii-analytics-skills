---
name: cloud-run-to-repo
description: Recover an existing deployed Cloud Run service into a git repo (uv-managed) with a repeatable deploy.sh. Use when a Cloud Run service was deployed ad-hoc (via `gcloud run deploy --source .` from the console or a lost working copy) and the user wants its source under version control with an easy redeploy script. Triggers on "create a repo from this Cloud Run service", "recover/adopt a Cloud Run service", "put this deployed service in git", "add a deploy script for this service".
---

# Cloud Run → Repo

Turn a deployed-but-unmanaged Cloud Run service into a git repo with reproducible,
uv-managed dependencies and a one-command `deploy.sh`.

## Preconditions

Confirm before starting; stop and ask the user to fix any that fail:
- `gcloud auth login` valid, and `gcloud config get-value project` is the right project.
- `git`, `gh` (authenticated), `uv`, `gsutil`, `unzip` available.
- You know: the **service name**, **region**, and where the repo should live (GitHub org/account, private/public).

## Workflow

1. **Recover the source.** Run the bundled script — it pulls the exact Cloud Build tarball
   and prints the live config you'll need:
   ```
   scripts/recover-source.sh SERVICE [REGION] [PROJECT] [DEST_DIR]
   ```
   If it reports no `build-source-location` (image deploy), use the image-extraction fallback
   in [REFERENCE.md](REFERENCE.md).

2. **Read the code.** Understand what it does before packaging it. Note the entry point.
   A non-empty `function-target` means it's a **Functions Framework** function (`main(request)`),
   *not* a plain web server — this drives the run command and build choice.

3. **Choose the build approach** — this is a real trade-off; present it and let the user decide.
   See [REFERENCE.md](REFERENCE.md) "Build approach". Default recommendation: **keep the buildpack
   (`--source .`) and use uv for local dev only**, generating `requirements.txt` from `uv.lock`.

4. **Set up uv.** Write `pyproject.toml` (pin `requires-python` to the service's runtime, e.g.
   `>=3.12,<3.13`) with the recovered deps; `uv lock`; export `requirements.txt`:
   ```
   uv export --no-hashes --no-emit-project --no-dev --format requirements-txt -o requirements.txt
   ```
   For a Functions Framework app, add `functions-framework` as a dependency (the buildpack adds it
   implicitly, but pinning it makes local `uv run functions-framework --target <fn>` work).

5. **Write `deploy.sh`.** Mirror every runtime flag from the recovered config so a redeploy can't
   silently reset it. Regenerate `requirements.txt` at the top so it never drifts. See the flag-mapping
   table and template in [REFERENCE.md](REFERENCE.md). Apply the **config policy**: non-secret env vars
   as literals; secrets via `--set-secrets` (Secret Manager), never committed.

6. **Verify locally** (no deploy): `uv sync` resolves, and the app imports / serves locally.

7. **Git + GitHub.** `.gitignore` (`.venv/`, `.env`, credential JSON), `README.md`,
   `git init -b main`, review `git ls-files` (no `.venv`/secrets), commit, then
   `gh repo create <name> --private --source . --remote origin --push`.

8. **Do NOT auto-deploy.** Redeploying mutates a live service. Hand `deploy.sh` back and let the
   user run it. Warn if the pinned `requirements.txt` differs from the floating buildpack build.

## Checklist

- [ ] Source recovered from the exact tarball (not reverse-engineered)
- [ ] Entry point / function-target identified
- [ ] Build approach chosen *with* the user
- [ ] `deploy.sh` mirrors live flags; secrets not literals
- [ ] `uv sync` + local run verified
- [ ] `git ls-files` clean; repo pushed
- [ ] Deploy left to the user
