"""Robust vertical vanishing point from long near-vertical edges over several frames.
Usage: vp_fit.py SRC out.npy f1,f2,...   Prints the roll (tilt of a true vertical at x=540 and at the subject x)."""
import cv2, numpy as np, sys
SRC=sys.argv[1]; OUT=sys.argv[2]; FR=[int(x) for x in sys.argv[3].split(",")]
SUBJ_X=float(sys.argv[4]) if len(sys.argv)>4 else 540
cap=cv2.VideoCapture(SRC); segs=[]
lsd=cv2.createLineSegmentDetector(cv2.LSD_REFINE_ADV)
for fr in FR:
    cap.set(cv2.CAP_PROP_POS_FRAMES, fr); ok,f=cap.read()
    if not ok: print("no frame",fr); continue
    g=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY)
    lines=lsd.detect(g)[0]
    if lines is None: continue
    for x1,y1,x2,y2 in lines.reshape(-1,4):
        L=np.hypot(x2-x1,y2-y1)
        if L<150: continue
        ang=np.degrees(np.arctan2(x2-x1, y2-y1)); ang=(ang+90)%180-90
        if abs(ang)<8: segs.append((x1,y1,x2,y2,L,ang,fr))
cap.release()
S=np.array(segs,float)
print(f"{len(S)} long near-vertical segments; tilt median {np.median(S[:,5]):+.2f} sd {S[:,5].std():.2f}")
for fr in FR:
    m=S[:,6]==fr; 
    if m.any(): print(f"  frame {fr}: {m.sum()} segs, median tilt {np.median(S[m,5]):+.2f}, left half {np.median(S[m&(S[:,0]<540),5]) if (m&(S[:,0]<540)).any() else float('nan'):+.2f}, right half {np.median(S[m&(S[:,0]>=540),5]) if (m&(S[:,0]>=540)).any() else float('nan'):+.2f}")
lines=[]
for x1,y1,x2,y2,L,a,fr in S:
    l=np.cross([x1,y1,1],[x2,y2,1]); lines.append(l/np.linalg.norm(l[:2]))
lines=np.array(lines); Ls=S[:,4]
best=None; rng=np.random.default_rng(0)
for _ in range(6000):
    i,j=rng.choice(len(lines),2,replace=False)
    v=np.cross(lines[i],lines[j])
    if abs(v[2])<1e-9: continue
    v=v/v[2]
    if abs(v[1])<1500: continue
    err=np.abs(lines@v)/np.sqrt(v[0]**2+v[1]**2+1e-9)
    inl=err<3.0; sc=(Ls*inl).sum()
    if best is None or sc>best[0]: best=(sc,v,inl)
sc,v,inl=best
print(f"RANSAC vertical VP at ({v[0]:.0f}, {v[1]:.0f}), inliers {inl.sum()}/{len(lines)}")
A=lines[inl]*Ls[inl,None]; _,_,Vt=np.linalg.svd(A); v2=Vt[-1]; v2=v2/v2[2]
print(f"refined vertical VP ({v2[0]:.0f}, {v2[1]:.0f}) -> taper over 1920 px = {1920/abs(v2[1])*100:.1f}%")
for x in (540, SUBJ_X, 100, 980):
    print(f"  tilt of a true vertical at x={x:.0f}: {np.degrees(np.arctan((x-v2[0])/(0-v2[1]))):+.2f} deg")
np.save(OUT, v2)
