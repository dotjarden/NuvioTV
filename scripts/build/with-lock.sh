#!/bin/bash
# NuvioTV build lock: run one command while holding the machine-wide BUILD lock, so two
# clones / agents never run xcodebuild or gradle at once (DerivedData and the Kotlin
# framework build do not survive concurrent runs). The lock is a flock on one file under
# ~/Claude/Projects, shared by every clone. Waits (no timeout) when another build holds it.
#
#   scripts/build/with-lock.sh xcodebuild -project … build
#
# Order rule: the SIMULATOR lock (with-sim-lock.sh) always wraps this one, never the
# reverse — build-lock-then-sim-lock deadlocks against a session holding the sim lock
# while it waits for a build.
LOCK="${BUILD_LOCK:-$HOME/Claude/Projects/.build.lock}"
exec python3 - "$LOCK" "$@" <<'PY'
import fcntl, os, subprocess, sys, time
lock, cmd = sys.argv[1], sys.argv[2:]
if not cmd:
    sys.exit("usage: with-lock.sh <command…>")
fd = os.open(lock, os.O_CREAT | os.O_RDWR, 0o644)
t0 = time.time()
try:
    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
except BlockingIOError:
    print(f"[with-lock] waiting for {lock}", file=sys.stderr, flush=True)
    fcntl.flock(fd, fcntl.LOCK_EX)
    print(f"[with-lock] acquired after {time.time() - t0:.0f} s", file=sys.stderr, flush=True)
os.write(fd, f"{os.getpid()} {' '.join(cmd)[:200]}\n".encode()); os.ftruncate(fd, os.lseek(fd, 0, os.SEEK_CUR))
sys.exit(subprocess.call(cmd))
PY
