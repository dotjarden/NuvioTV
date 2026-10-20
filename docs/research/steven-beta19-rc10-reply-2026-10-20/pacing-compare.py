import re, sys, statistics
def load(p):
    t=[];s=[];cur=None
    for line in open(p):
        m=re.search(r'pts_time:([\d.]+)',line)
        if m: cur=float(m.group(1)); continue
        m=re.search(r'scene_score=([\d.]+)',line)
        if m: t.append(cur); s.append(float(m.group(1)))
    return t,s
def stats(name,p):
    t,s=load(p); n=len(s); thr=0.008
    bursts=[]; i=0
    while i<n:
        if s[i]>=thr:
            j=i
            while j<n and s[j]>=thr*0.3: j+=1
            if 4<=j-i<=15: bursts.append(s[i:j])
            i=j
        else: i+=1
    dips=0; maxshare=[]; nonmono=0
    for seq in bursts:
        d=any(seq[k]<0.25*((seq[k-1]+seq[k+1])/2) and (seq[k-1]+seq[k+1])/2>=thr for k in range(1,len(seq)-1))
        dips+=d
        maxshare.append(max(seq)/sum(seq))
        # count re-accelerations: a frame > 2x the previous after the peak
        pk=seq.index(max(seq)); nonmono+=any(seq[k]>2*seq[k-1] and seq[k]>=thr for k in range(pk+1,len(seq)))
    print(f"{name}: {len(bursts)} short bursts, dips in {dips} ({100*dips/len(bursts):.0f}%), re-accel after peak in {nonmono} ({100*nonmono/len(bursts):.0f}%), median max-step share {statistics.median(maxshare):.2f}")
stats("rc10 IMG_9057", sys.argv[1]); stats("rc9 IMG_9025", sys.argv[2])
