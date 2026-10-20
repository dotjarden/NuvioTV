import re, sys
t=[];s=[];cur=None
for line in open(sys.argv[1]):
    m=re.search(r'pts_time:([\d.]+)',line)
    if m: cur=float(m.group(1)); continue
    m=re.search(r'scene_score=([\d.]+)',line)
    if m: t.append(cur); s.append(float(m.group(1)))
n=len(s); thr=0.008
bursts=[]; i=0
while i<n:
    if s[i]>=thr:
        j=i
        while j<n and s[j]>=thr*0.3: j+=1
        if j-i>=4: bursts.append((i,j))
        i=j
    else: i+=1
print("bursts", len(bursts))
flag=0
for i,j in bursts:
    seq=s[i:j]
    dips=[]
    for k in range(1,len(seq)-1):
        nb=(seq[k-1]+seq[k+1])/2
        if nb>=thr and seq[k]<0.25*nb: dips.append(k)
    dur=(j-i)/30
    if dips:
        flag+=1
        print(f"{int(t[i]//60)}:{t[i]%60:05.2f} len {j-i} fr ({dur:.2f}s) dips at +{[round(d/30,2) for d in dips]} s  seq {[round(x*1000) for x in seq]}")
print("bursts with dips", flag)
