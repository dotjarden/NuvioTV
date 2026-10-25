#!/bin/bash
# Nuvio iOS release watch: has NuvioMedia/NuvioMobile published a new release?
#
#   scripts/ios/check-release.sh [--quiet] [--no-notify]
#
# Reads the GitHub releases list (gh if signed in, anonymous curl otherwise), compares the
# newest non-draft release (prereleases count) with the watermark in
# ~/.config/nuvio-ipad/last-release, and for every release newer than the watermark:
#   - appends the tag, date, link, assets and release notes to docs/ios-release-watch.md
#   - posts one macOS notification naming the version and the first line of its notes
# It always writes the newest tag to ~/.config/nuvio-ipad/latest-release so that
# scripts/ios/refresh-ipad.sh can read it without a second GitHub call.
#
#   exit 0  new release(s) found and logged
#   exit 3  nothing new since the watermark
#   exit 2  GitHub unreachable or unparseable (nothing written)
#
#   --quiet      print only the NEW/LATEST line
#   --no-notify  skip the macOS notification (still logs and moves the watermark)
#   --init       set the watermark to the newest release without logging or notifying
#
# Release notes are third-party text copied verbatim into the log; they are never rewritten.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
CONF_DIR="${NUVIO_IPAD_CONF:-$HOME/.config/nuvio-ipad}"
CONF="$CONF_DIR/config.env"
UPSTREAM_REPO=NuvioMedia/NuvioMobile
[ -f "$CONF" ] && . "$CONF"

WATERMARK="$CONF_DIR/last-release"
LATEST_FILE="$CONF_DIR/latest-release"
LOG_MD="$ROOT/docs/ios-release-watch.md"

QUIET=0; NOTIFY=1; INIT=0
for a in "$@"; do
  case "$a" in
    --quiet) QUIET=1 ;;
    --no-notify) NOTIFY=0 ;;
    --init) INIT=1 ;;
    -h|--help) sed -n '2,24p' "$0"; exit 0 ;;
    *) echo "unknown flag: $a" >&2; exit 2 ;;
  esac
done
mkdir -p "$CONF_DIR"

say() { [ "$QUIET" = 1 ] || echo "$*"; }

fetch_releases() {
  local url="repos/$UPSTREAM_REPO/releases?per_page=15"
  if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
    gh api "$url" 2>/dev/null && return 0
  fi
  curl -fsSL --max-time 30 -H "Accept: application/vnd.github+json" "https://api.github.com/$url"
}

JSON="$(fetch_releases)" || { echo "REFUSED: GitHub unreachable" >&2; exit 2; }
[ -n "$JSON" ] || { echo "REFUSED: empty response" >&2; exit 2; }

SEEN="$(cat "$WATERMARK" 2>/dev/null || true)"

# Emit one record per release newer than the watermark, oldest first, as
#   tag \x1f name \x1f published \x1f url \x1f assets \x1f body-escaped
# followed by a final line "LATEST <tag>". Python runs isolated (-I) on data only.
JSON_FILE="$(mktemp "${TMPDIR:-/tmp}/nuvio-releases.XXXXXX")"
trap 'rm -f "$JSON_FILE"' EXIT
printf '%s' "$JSON" > "$JSON_FILE"
RECORDS="$(SEEN_TAG="$SEEN" python3 -I - "$JSON_FILE" <<'PY'
import json, os, sys
with open(sys.argv[1], encoding="utf-8") as fh:
    rel = [r for r in json.load(fh) if not r.get("draft")]
if not rel:
    sys.exit(2)
seen = os.environ.get("SEEN_TAG", "")
new = []
for r in rel:
    if r["tag_name"] == seen:
        break
    new.append(r)
if seen == "":
    new = new[:1]  # first run: log only the newest release, not the whole history
for r in reversed(new):
    assets = ", ".join(a["name"] for a in r.get("assets", []))
    body = (r.get("body") or "").replace("\\", "\\\\").replace("\n", "\\n")
    print("\x1f".join([r["tag_name"], r.get("name") or r["tag_name"],
                       r.get("published_at") or "", r.get("html_url") or "", assets, body]))
print("LATEST\t" + rel[0]["tag_name"])
PY
)" || { echo "REFUSED: could not parse releases" >&2; exit 2; }

LATEST="$(printf '%s\n' "$RECORDS" | awk -F'\t' '/^LATEST\t/{print $2}')"
[ -n "$LATEST" ] || { echo "REFUSED: no release in list" >&2; exit 2; }
printf '%s\n' "$LATEST" > "$LATEST_FILE"

if [ "$INIT" = 1 ]; then
  printf '%s\n' "$LATEST" > "$WATERMARK"
  say "INIT watermark = $LATEST"
  exit 0
fi

NEW_COUNT=0
while IFS=$'\x1f' read -r tag name published url assets body; do
  [ -n "$tag" ] || continue
  [ "$tag" = "LATEST	$LATEST" ] && continue
  case "$tag" in LATEST*) continue ;; esac
  NEW_COUNT=$((NEW_COUNT + 1))
  day="${published%%T*}"
  {
    [ -s "$LOG_MD" ] || printf '# Nuvio iOS release watch\n\nAppended by `scripts/ios/check-release.sh` (daily via the nuvio-ipad launch agent). Newest at the bottom. Notes are upstream'\''s own text.\n'
    printf '\n## %s — %s\n\n%s\n\nAssets: %s\n\n' "$tag" "$day" "$url" "${assets:-none}"
    printf '%b\n' "$body" | sed 's/^/> /'
  } >> "$LOG_MD"
  first_line="$(printf '%b' "$body" | grep -m1 -vE '^\s*$' | cut -c1-120)"
  say "NEW $tag ($day) $url"
  if [ "$NOTIFY" = 1 ]; then
    osascript -e "display notification \"${first_line//\"/\\\"}\" with title \"Nuvio iOS release $tag\" subtitle \"Notes appended to docs/ios-release-watch.md\"" >/dev/null 2>&1 || true
  fi
done <<< "$RECORDS"

if [ "$NEW_COUNT" = 0 ]; then
  say "LATEST $LATEST (seen)"
  exit 3
fi
printf '%s\n' "$LATEST" > "$WATERMARK"
exit 0
