#!/usr/bin/env bash
#
# Recover the source of a source-deployed Cloud Run service from its Cloud Build
# staging tarball, and print the facts needed to reconstruct deploy.sh.
#
# Usage:
#   recover-source.sh SERVICE [REGION] [PROJECT] [DEST_DIR]
#
# REGION/PROJECT default to the active gcloud config. DEST_DIR defaults to ./<SERVICE>-src.
# Requires: gcloud (authenticated), gsutil, unzip.
#
set -euo pipefail

SERVICE="${1:?usage: recover-source.sh SERVICE [REGION] [PROJECT] [DEST_DIR]}"
REGION="${2:-$(gcloud config get-value run/region 2>/dev/null || true)}"
REGION="${REGION:-$(gcloud config get-value compute/region 2>/dev/null || true)}"
PROJECT="${3:-$(gcloud config get-value project 2>/dev/null)}"
DEST_DIR="${4:-./${SERVICE}-src}"

if [[ -z "${REGION}" ]]; then
  echo "ERROR: no region given and none in gcloud config. Pass REGION as arg 2." >&2
  exit 2
fi

echo ">> Service : ${SERVICE}"
echo ">> Region  : ${REGION}"
echo ">> Project : ${PROJECT}"

describe() {
  gcloud run services describe "${SERVICE}" \
    --region "${REGION}" --project "${PROJECT}" \
    --format="value(${1})" 2>/dev/null || true
}

SRC="$(describe "metadata.annotations['run.googleapis.com/build-source-location']")"

if [[ -z "${SRC}" ]]; then
  cat >&2 <<EOF

ERROR: no 'build-source-location' annotation on this service.
It was NOT deployed from source (likely a prebuilt container image).
Fall back to image extraction — see REFERENCE.md "Image-extraction fallback".
Deployed image:
  $(describe "spec.template.spec.containers[0].image")
EOF
  exit 3
fi

echo ">> Source tarball: ${SRC}"
mkdir -p "${DEST_DIR}"
TMP_ZIP="$(mktemp -t crun-src-XXXXXX).zip"
# The annotation may carry a #<generation> suffix; gsutil cp honors it (pins exact version).
gsutil cp "${SRC}" "${TMP_ZIP}"
unzip -o "${TMP_ZIP}" -d "${DEST_DIR}" >/dev/null
rm -f "${TMP_ZIP}"
echo ">> Extracted to: ${DEST_DIR}"
echo ">> Files:"
ls -1 "${DEST_DIR}" | sed 's/^/     /'

# --- Facts for reconstructing deploy.sh -------------------------------------
echo ""
echo ">> ===== Service config (map these into deploy.sh) ====="
echo ">> function-target : $(describe "metadata.annotations['run.googleapis.com/build-function-target']") (empty = plain web server, not a function)"
echo ">> service-account : $(describe "spec.template.spec.serviceAccountName")"
echo ">> cpu / memory    : $(describe "spec.template.spec.containers[0].resources.limits.cpu") / $(describe "spec.template.spec.containers[0].resources.limits.memory")"
echo ">> concurrency     : $(describe "spec.template.spec.containerConcurrency")"
echo ">> timeout (s)     : $(describe "spec.template.spec.timeoutSeconds")"
echo ">> max-instances   : $(describe "metadata.annotations['run.googleapis.com/maxScale']")"
echo ">> ingress         : $(describe "metadata.annotations['run.googleapis.com/ingress']")"
echo ">> invoker-iam-disabled (true => --allow-unauthenticated): $(describe "metadata.annotations['run.googleapis.com/invoker-iam-disabled']")"
echo ""
echo ">> Env vars (sort into deploy.sh literals vs Secret Manager --set-secrets):"
gcloud run services describe "${SERVICE}" --region "${REGION}" --project "${PROJECT}" \
  --format="value(spec.template.spec.containers[0].env)" 2>/dev/null | sed 's/^/     /'
echo ""
echo ">> Check for a Cloud Scheduler trigger:"
gcloud scheduler jobs list --project "${PROJECT}" --location "${REGION}" \
  --format="value(name,schedule)" 2>/dev/null | grep -i "${SERVICE}" | sed 's/^/     /' \
  || echo "     (none in ${REGION}; also check other locations)"
