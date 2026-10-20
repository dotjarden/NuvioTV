#!/usr/bin/env python3
"""Summarise an exported Time Profiler table (xctrace export, id/ref aware): main-thread self and inclusive symbols in a window."""
import sys, collections, xml.etree.ElementTree as ET
xmlpath=sys.argv[1]; t0=float(sys.argv[2]); t1=float(sys.argv[3])
root=ET.parse(xmlpath).getroot()
refs={}
def reg(el):
    i=el.get("id")
    if i: refs[i]=el
    for c in el: reg(c)
def res(el):
    if el is None: return None
    r=el.get("ref")
    return refs.get(r) if r else el
def frames(bt):
    bt=res(bt)
    out=[]
    if bt is None: return out
    for f in bt.findall("frame"):
        f=res(f); b=res(f.find("binary")) if f is not None else None
        out.append((f.get("name") or "?", (b.get("name") if b is not None else "?")))
    return out
main=0; total=0; selfc=collections.Counter(); incl=collections.Counter(); inclApp=collections.Counter(); topApp=collections.Counter(); binaries=collections.Counter()
for row in root.iter("row"):
    reg(row)
    st=res(row.find("sample-time")); th=res(row.find("thread")); state=res(row.find("thread-state"))
    if st is None or th is None: continue
    t=int(st.text)/1e9
    if not (t0<=t<=t1): continue
    total+=1
    if not (th.get("fmt") or "").startswith("Main Thread"): continue
    if state is not None and (state.get("fmt") or "")!="Running": continue
    main+=1
    fr=frames(row.find("tagged-backtrace"))
    if not fr: continue
    selfc[fr[0]]+=1; binaries[fr[0][1]]+=1
    seen=set()
    for name,bin in fr:
        key=(name,bin)
        if key in seen: continue
        seen.add(key); incl[key]+=1
        if bin=="NuvioTV": inclApp[name]+=1
    app=[n for n,b in fr if b=="NuvioTV"]
    if app: topApp[app[0]]+=1
print(f"window {t0}-{t1}s: samples={total} main-thread running={main} ({main/(t1-t0)*1.0:.0f}/s of 1000)")
print("\n== self, by binary"); [print(f"  {c:5} {b}") for b,c in binaries.most_common(8)]
print("\n== self frames (top 14)"); [print(f"  {c:5} {n[:100]}  [{b}]") for (n,b),c in selfc.most_common(14)]
print("\n== heaviest NuvioTV frame nearest the top of each stack (top 20)"); [print(f"  {c:5} {n[:120]}") for n,c in topApp.most_common(20)]
print("\n== inclusive NuvioTV symbols (top 25)"); [print(f"  {c:5} {n[:120]}") for n,c in inclApp.most_common(25)]
