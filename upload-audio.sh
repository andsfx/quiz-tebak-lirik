#!/usr/bin/env bash
set -euo pipefail

# Upload MP3 files from ./audio to Cloudflare R2 path used by app.
# Requires one of:
#   1) wrangler logged in: npx wrangler r2 object put <bucket>/<key> --file <file>
#   2) env BUCKET=... plus Wrangler auth envs already configured

BUCKET="${BUCKET:-cdn}"
PREFIX="${PREFIX:-quiz-tebak-lirik/audio}"
AUDIO_DIR="${AUDIO_DIR:-audio}"
CONCURRENCY="${CONCURRENCY:-4}"

if ! command -v npx >/dev/null 2>&1; then
  echo "npx not found" >&2
  exit 1
fi

if [ ! -d "$AUDIO_DIR" ]; then
  echo "Audio dir not found: $AUDIO_DIR" >&2
  exit 1
fi

mapfile -t files < <(find "$AUDIO_DIR" -maxdepth 1 -type f -name '*.mp3' | sort)
if [ "${#files[@]}" -eq 0 ]; then
  echo "No MP3 files in $AUDIO_DIR"
  exit 0
fi

upload_one(){
  local file="$1"
  local name
  name="$(basename "$file")"
  local key="$PREFIX/$name"
  echo "Uploading $file -> r2://$BUCKET/$key"
  npx --yes wrangler r2 object put "$BUCKET/$key" --file "$file" --content-type audio/mpeg
}
export -f upload_one
export BUCKET PREFIX

printf '%s\0' "${files[@]}" | xargs -0 -n1 -P "$CONCURRENCY" bash -c 'upload_one "$0"'

echo "Done. CDN base: https://cdn.andotherstori.my.id/$PREFIX/"
