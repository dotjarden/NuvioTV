import sys, subprocess, re
# Detail-walk window per trace = the dense hitch band after the launch (first second >= 15 with hitches .. last), widened by 2 s.
tr=sys.argv[1]
out=subprocess.run(["python3","-I","docs/research/batch-p-wave0-2026-10-20/hitches.py",tr],capture_output=True,text=True).stdout
secs=[int(a) for a,b in re.findall(r"(\d+):(\d+)", out.split("per-second (app):")[1].split("\n")[0])] if "per-second" in out else []
secs=[s for s in secs if s>=15]
if secs: print(f"{secs[0]-2}-{secs[-1]+2}")
else: print("0-0")
