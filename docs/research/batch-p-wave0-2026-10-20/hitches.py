#!/usr/bin/env python3
"""Summarise an Animation Hitches trace: count, total ms, max ms, per second of run (xctrace export id/ref aware)."""
import sys, subprocess, collections, xml.etree.ElementTree as ET
tr = sys.argv[1]
xml = subprocess.run(["xcrun","xctrace","export","--input",tr,"--xpath",'/trace-toc/run[@number="1"]/data/table[@schema="hitches"]'],capture_output=True,text=True).stdout
root = ET.fromstring(xml)
refs = {}
def val(el):
    if el is None: return None
    if el.get("ref"): return refs.get(el.get("ref"))
    v = (el.get("fmt"), el.text)
    if el.get("id"): refs[el.get("id")] = v
    return v
rows=[]
for row in root.iter("row"):
    kids=list(row)
    st=val(row.find("start-time")); du=val(row.find("duration")); pr=val(row.find("process")); strings=[val(s) for s in row.findall("string")]
    for k in kids: val(k)  # register ids in order
    if not st or not du or st[1] is None or du[1] is None: continue
    rows.append((int(st[1])/1e9, int(du[1])/1e6, (pr[0] if pr and pr[0] else "?"), (strings[-1][0] if strings and strings[-1] and strings[-1][0] else "")[:90]))
app=[r for r in rows if r[2].startswith("NuvioTV")]
print(f"hitches total={len(rows)} app={len(app)} app_ms={sum(r[1] for r in app):.0f} max_ms={max([r[1] for r in app] or [0]):.1f}")
bysec=collections.Counter(int(r[0]) for r in app)
print("per-second (app):", " ".join(f"{s}:{bysec[s]}" for s in sorted(bysec)))
for r in sorted(app,key=lambda r:-r[1])[:6]: print(f"  {r[0]:6.2f}s {r[1]:6.1f}ms {r[3]}")
