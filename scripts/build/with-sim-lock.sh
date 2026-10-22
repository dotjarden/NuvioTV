#!/bin/bash
# NuvioTV simulator lock: run one command while holding the machine-wide SIMULATOR lock, so
# two clones / agents never drive the FA87 fixture simulator at once (a UI run from one clone
# SIGKILLs the other's; 2026-10-21). The lock is a flock on one file under
# ~/Claude/Projects, shared by every clone. Waits (no timeout) when another build holds it.
#
#   scripts/build/with-lock.sh xcodebuild -project … build
#
# Order rule: this lock always wraps the BUILD lock (with-lock.sh), never the reverse —
# build-lock-then-sim-lock deadlocks against a session holding the sim lock while it waits
# for a build.
LOCK="${SIM_LOCK:-$HOME/Claude/Projects/.sim-FA87.lock}"
exec python3 - "$LOCK" "$@" <<'PY'
import fcntl, os, subprocess, sys, time
lock, cmd = sys.argv[1], sys.argv[2:]
if not cmd:
    sys.exit("usage: with-sim-lock.sh <command…>")
fd = os.open(lock, os.O_CREAT | os.O_RDWR, 0o644)
t0 = time.time()
try:
    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
except BlockingIOError:
    print(f"[with-sim-lock] waiting for {lock}", file=sys.stderr, flush=True)
    fcntl.flock(fd, fcntl.LOCK_EX)
    print(f"[with-sim-lock] acquired after {time.time() - t0:.0f} s", file=sys.stderr, flush=True)
os.write(fd, f"{os.getpid()} {' '.join(cmd)[:200]}\n".encode()); os.ftruncate(fd, os.lseek(fd, 0, os.SEEK_CUR))
sys.exit(subprocess.call(cmd))
PY
