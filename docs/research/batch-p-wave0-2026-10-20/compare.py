#!/usr/bin/env python3
import sys,subprocess,xml.etree.ElementTree as ET
def rows(tr):
    xml=subprocess.run(["xcrun","xctrace","export","--input",tr,"--xpath",'/trace-toc/run[@number="1"]/data/table[@schema="hitches"]'],capture_output=True,text=True).stdout
    root=ET.fromstring(xml); refs={}; out=[]
    def val(el):
        if el is None: return None
        if el.get("ref"): return refs.get(el.get("ref"))
        v=(el.get("fmt"),el.text)
        if el.get("id"): refs[el.get("id")]=v
        return v
    for row in root.iter("row"):
        st=val(row.find("start-time")); du=val(row.find("duration"))
        for k in row: val(k)
        if st and du and st[1] and du[1]: out.append((int(st[1])/1e9,int(du[1])/1e6))
    return out
a,b=float(sys.argv[1]),float(sys.argv[2])
print(f"{'run':44} {'hitches':>7} {'ms':>6} {'max':>5} {'>=100ms':>7}  (window {a:.0f}–{b:.0f} s)")
for tr in sys.argv[3:]:
    r=[x for x in rows(tr) if a<=x[0]<=b]
    print(f"{tr.split('/')[-1].replace('.trace',''):44} {len(r):7} {sum(x[1] for x in r):6.0f} {max([x[1] for x in r] or [0]):5.0f} {sum(1 for x in r if x[1]>=100):7}")
