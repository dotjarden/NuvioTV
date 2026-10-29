#!/usr/bin/env bash
# graph-impact.sh — map a NuvioMobile diff onto graphify communities.
#
# Prints which subsystems (graph communities) a change touches, for the
# batch doc and the review brief. Reads the local tree-sitter graph at
# NuvioMobile/graphify-out/graph.json (or $GRAPHIFY_OUT/graph.json); no LLM.
#
# Usage (refs are NuvioMobile refs):
#   scripts/graph-impact.sh <base> [<head>]   # diff base..head (head defaults to HEAD)
#   scripts/graph-impact.sh --staged          # index vs HEAD
#   scripts/graph-impact.sh --worktree        # working tree vs HEAD
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SUB="$ROOT/NuvioMobile"
OUT="${GRAPHIFY_OUT:-NuvioMobile/graphify-out}"
case "$OUT" in /*) ;; *) OUT="$ROOT/$OUT" ;; esac
GRAPH="$OUT/graph.json"

if [ ! -f "$GRAPH" ]; then
  echo "graph-impact: no graph at $GRAPH (run: cd NuvioMobile && graphify extract . --code-only)" >&2
  exit 2
fi

case "${1:-}" in
  --staged)   files="$(git -C "$SUB" diff --name-only --cached)"; label="staged" ;;
  --worktree) files="$(git -C "$SUB" diff --name-only)";          label="worktree" ;;
  ""|-h|--help)
    sed -n '2,12p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
  *)
    base="$1"; head="${2:-HEAD}"
    files="$(git -C "$SUB" diff --name-only "$base" "$head")"; label="$base..$head" ;;
esac

head_sha="$(git -C "$SUB" rev-parse --short=8 HEAD)"

# The file list goes through a temp file: the Python body below is a heredoc,
# which would otherwise take over stdin and hide a piped list.
list_file="$(mktemp -t graph-impact)"
trap 'rm -f "$list_file"' EXIT
printf '%s\n' "$files" > "$list_file"

python3 -I - "$GRAPH" "$label" "$head_sha" "$list_file" <<'PY'
import json, sys, collections
graph_path, label, head_sha, list_file = sys.argv[1:5]
changed = [l.strip() for l in open(list_file) if l.strip()]
g = json.load(open(graph_path))
built = (g.get("built_at_commit") or "")[:8]

by_file = collections.defaultdict(list)
per_comm_total = collections.Counter()
names = {}
for n in g["nodes"]:
    c = n.get("community")
    if c is None:
        continue
    per_comm_total[c] += 1
    names[c] = n.get("community_name") or f"Community {c}"
    sf = n.get("source_file")
    if sf:
        by_file[sf].append(n)

hit = collections.defaultdict(lambda: {"symbols": 0, "files": set()})
unmapped = []
for f in changed:
    nodes = by_file.get(f)
    if not nodes:
        unmapped.append(f)
        continue
    for n in nodes:
        c = n["community"]
        hit[c]["symbols"] += 1
        hit[c]["files"].add(f)

print(f"## Graph impact: {label}")
stale = built and built != head_sha[:len(built)]
print(f"- graph built at `{built or '?'}`, submodule HEAD `{head_sha}`"
      + ("  **(graph is stale: run `graphify update .` in NuvioMobile/)**" if stale else ""))
print(f"- {len(changed)} changed file(s), {len(hit)} communit{'y' if len(hit)==1 else 'ies'} touched")
print()
if hit:
    print("| Community | Symbols touched / in community | Files |")
    print("|---|---|---|")
    for c, d in sorted(hit.items(), key=lambda kv: -kv[1]["symbols"]):
        fl = sorted(d["files"])
        shown = ", ".join(f"`{x}`" for x in fl[:4]) + (f" (+{len(fl)-4} more)" if len(fl) > 4 else "")
        print(f"| {names[c]} | {d['symbols']} / {per_comm_total[c]} | {shown} |")
if unmapped:
    print()
    print(f"Not in the graph ({len(unmapped)}): " + ", ".join(f"`{x}`" for x in unmapped[:12])
          + (f" (+{len(unmapped)-12} more)" if len(unmapped) > 12 else ""))
PY
