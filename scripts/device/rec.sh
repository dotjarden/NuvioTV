#!/bin/bash
# NuvioTV device rig: record the Living Room Apple TV's screen.
#   rec.sh start [path.mp4]     # background recording, pid in $REC_PIDFILE
#   rec.sh stop                 # stop it (SIGINT) and print the file
#   rec.sh for <seconds> [path] # fixed-length recording in the foreground
#   rec.sh frames <mp4> [fps]   # sample frames with ffmpeg into <mp4>.frames/ (default 4 fps)
#
# Backend order: `devicectl device capture screen-record` when the box supports it, else the
# Mac's AVFoundation capture device for the Apple TV (the same source QuickTime's "Movie
# Recording" offers for a paired Apple TV), else a screenshot burst (~0.7 fps; the honest
# fallback, not a motion judgment). Set REC_BACKEND=devicectl|avf|burst to force one.
set -euo pipefail
CONF="${NUVIOTV_DEVICE_CONF:-$HOME/.config/nuviotv-device}"
# shellcheck disable=SC1091
source "$CONF/atv.env"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REC_PIDFILE="${REC_PIDFILE:-$CONF/rec.pid}"
default_out() { local d="$ROOT/docs/research/device-rig-$(date +%F)"; mkdir -p "$d"; echo "$d/rec-$(date +%H%M%S).mp4"; }

avf_index() {
  # "[n] Living Room" in ffmpeg's avfoundation device list
  ffmpeg -hide_banner -f avfoundation -list_devices true -i "" 2>&1 | grep -m1 -E "\[[0-9]+\] $ATV_NAME" | sed -E 's/.*\[([0-9]+)\] .*/\1/'
}
pick_backend() {
  if [[ -n "${REC_BACKEND:-}" ]]; then echo "$REC_BACKEND"; return; fi
  if [[ -f "$CONF/rec.backend" ]]; then cat "$CONF/rec.backend"; return; fi
  local probe; probe="$(xcrun devicectl device capture screen-record --device "$ATV_UDID" --destination /tmp/nuviotv-rec-probe.mp4 --duration 1 2>&1 || true)"
  if ! grep -q "not supported by this device" <<<"$probe"; then echo devicectl | tee "$CONF/rec.backend"; return; fi
  if [[ -n "$(avf_index)" ]]; then echo avf | tee "$CONF/rec.backend"; return; fi
  echo burst | tee "$CONF/rec.backend"
}
start_rec() {
  local out="$1" backend; backend="$(pick_backend)"; echo "backend=$backend" >&2
  case "$backend" in
    devicectl) xcrun devicectl device capture screen-record --device "$ATV_UDID" --destination "$out" ${2:+--duration $2} ;;
    avf) local idx; idx="$(avf_index)"
         ffmpeg -hide_banner -loglevel error -y -f avfoundation -framerate 30 -capture_raw_data false -i "$idx:none" \
           ${2:+-t $2} -c:v libx264 -preset veryfast -pix_fmt yuv420p "$out" ;;
    burst) # ~0.7 fps: devicectl screenshots take ~1.3-4 s each, so REC_WORKERS (default 4) run in parallel
         local dir="${out%.mp4}.burst"; mkdir -p "$dir"; local end=$(( $(date +%s) + ${2:-3600} )) w
         for ((w = 0; w < ${REC_WORKERS:-4}; w++)); do
           ( while (( $(date +%s) < end )); do
               xcrun devicectl device capture screenshot --device "$ATV_UDID" --destination "$dir/$(python3 -c 'import time;print(int(time.time()*1000))').png" -q >/dev/null 2>&1 || true
             done ) &
         done; wait
         # name = capture completion ms; the clip plays at 1 frame per captured frame (timestamps in frames.tsv)
         ls "$dir"/*.png | sed -E 's#.*/([0-9]+)\.png#\1#' | awk 'NR==1{t0=$1} {printf "%d\t%.2f\n", $1, ($1-t0)/1000}' > "$dir/frames.tsv"
         ffmpeg -hide_banner -loglevel error -y -framerate 1 -pattern_type glob -i "$dir/*.png" -vf scale=1920:-2 -pix_fmt yuv420p "$out" ;;
  esac
}
cmd="${1:-}"; shift || true
case "$cmd" in
  start)
    out="${1:-$(default_out)}"; echo "$out" > "$REC_PIDFILE.path"
    ( start_rec "$out" ) & echo $! > "$REC_PIDFILE"; echo "recording to $out (pid $(cat "$REC_PIDFILE"))" ;;
  stop)
    pid="$(cat "$REC_PIDFILE")"; pkill -INT -P "$pid" 2>/dev/null || true; kill -INT "$pid" 2>/dev/null || true
    while kill -0 "$pid" 2>/dev/null; do sleep 0.5; done; sleep 1; cat "$REC_PIDFILE.path"; rm -f "$REC_PIDFILE" "$REC_PIDFILE.path" ;;
  for)
    secs="${1:?seconds}"; out="${2:-$(default_out)}"; start_rec "$out" "$secs"; echo "$out" ;;
  frames)
    mp4="${1:?mp4}"; fps="${2:-4}"; dir="${mp4%.mp4}.frames"; mkdir -p "$dir"
    ffmpeg -hide_banner -loglevel error -y -i "$mp4" -vf "fps=$fps,scale=960:-2" "$dir/f%04d.png"; ls "$dir" | wc -l | xargs echo "frames in $dir:" ;;
  *) sed -n 2,11p "$0"; exit 64 ;;
esac
