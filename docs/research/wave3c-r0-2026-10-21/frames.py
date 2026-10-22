#!/usr/bin/env python3
# Per-frame GPU / render / offscreen-pass stats from an Animation Hitches trace, over the windows given as "a-b" seconds (written by the BUG-206 cause hunt, 2026-10-22).
import sys,subprocess,xml.etree.ElementTree as ET,statistics,collections
tr=sys.argv[1]; wins=[tuple(map(float,w.split("-"))) for w in sys.argv[2:]]
def table(name):
    xml=subprocess.run(["xcrun","xctrace","export","--input",tr,"--xpath",f'/trace-toc/run[@number="1"]/data/table[@schema="{name}"]'],capture_output=True,text=True).stdout
    root=ET.fromstring(xml); refs={}
    cols=[c.find("mnemonic").text for c in root.iter("col")]
    out=[]
    for row in root.iter("row"):
        vals=[]
        for k in row:
            if k.get("ref"): vals.append(refs.get(k.get("ref")))
            else:
                v=(k.get("fmt"),k.text)
                if k.get("id"): refs[k.get("id")]=v
                vals.append(v)
        out.append(dict(zip(cols,vals)))
    return out
def num(v): 
    return int(v[1]) if v and v[1] not in (None,"") else None
R={};G={};U={}
for d in table("hitches-renders"):
    sid=num(d.get("swap-id")); 
    if sid is None: continue
    R[sid]=(num(d["start"])/1e9, num(d["duration"])/1e6 if num(d["duration"]) else 0, num(d.get("offscreen-passes")) or 0)
for d in table("hitches-gpu"):
    sid=num(d.get("swap-id"))
    if sid is None or num(d["duration"]) is None: continue
    G[sid]=G.get(sid,0)+num(d["duration"])/1e6
for d in table("hitches-updates"):
    sid=num(d.get("swap-id"))
    if sid is None or num(d["duration"]) is None: continue
    U[sid]=U.get(sid,0)+num(d["duration"])/1e6
def pct(a,p):
    a=sorted(a); 
    return a[min(len(a)-1,int(len(a)*p))] if a else 0
for a,b in wins:
    sids=[s for s,(t,_,_) in R.items() if a<=t<=b]
    g=[G.get(s,0) for s in sids]; r=[R[s][1] for s in sids]; o=[R[s][2] for s in sids]; u=[U.get(s,0) for s in sids]
    if not sids: print(f"{a}-{b}: no frames"); continue
    print(f"{a:5.1f}-{b:5.1f}s frames={len(sids):4}  gpu ms med/p90/max={pct(g,.5):5.1f}/{pct(g,.9):5.1f}/{max(g):5.1f}  render ms med/p90/max={pct(r,.5):5.1f}/{pct(r,.9):5.1f}/{max(r):5.1f}  offscreen med/p90/max={pct(o,.5)}/{pct(o,.9)}/{max(o)}  app-update ms p90/max={pct(u,.9):5.1f}/{max(u):5.1f}  gpu>14ms={sum(1 for x in g if x>14)}")
