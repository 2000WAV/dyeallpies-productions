"""Robust vertical vanishing point from long near-vertical edges, over several clean frames."""
import cv2, numpy as np
SP=r"C:/Users/Dennis/AppData/Local/Temp/claude/c--Users-Dennis-Desktop-usf-projects-design/76c6b591-9dae-48f4-a9a6-1c3fe4a6bdb1/scratchpad"
cap=cv2.VideoCapture("IMG_5990.MOV")
segs=[]
lsd=cv2.createLineSegmentDetector(cv2.LSD_REFINE_ADV)
for fr in (10, 40, 60, 1980, 2010):
    cap.set(cv2.CAP_PROP_POS_FRAMES, fr); ok,f=cap.read()
    if not ok: continue
    g=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY)
    lines=lsd.detect(g)[0]
    if lines is None: continue
    for x1,y1,x2,y2 in lines.reshape(-1,4):
        L=np.hypot(x2-x1,y2-y1)
        if L<150: continue
        ang=np.degrees(np.arctan2(x2-x1, y2-y1))   # from vertical
        ang=(ang+90)%180-90
        if abs(ang)<8: segs.append((x1,y1,x2,y2,L,ang,fr))
cap.release()
S=np.array(segs,float)
print(f"{len(S)} long near-vertical segments; tilt median {np.median(S[:,5]):+.2f} sd {S[:,5].std():.2f}")
# line in homogeneous coords
lines=[]
for x1,y1,x2,y2,L,a,fr in S:
    l=np.cross([x1,y1,1],[x2,y2,1]); lines.append(l/np.linalg.norm(l[:2])); 
lines=np.array(lines); Ls=S[:,4]
best=None
rng=np.random.default_rng(0)
for _ in range(4000):
    i,j=rng.choice(len(lines),2,replace=False)
    v=np.cross(lines[i],lines[j])
    if abs(v[2])<1e-9: continue
    v=v/v[2]
    if abs(v[1])<1500: continue                      # a plausible vertical VP is far away
    d=np.abs(lines@v)/np.maximum(np.linalg.norm(v[:2]),1e-9)   # ~point-line distance scaled
    err=np.abs((lines@v))/np.sqrt(v[0]**2+v[1]**2+1e-9)
    inl=err<3.0
    sc=(Ls*inl).sum()
    if best is None or sc>best[0]: best=(sc,v,inl)
sc,v,inl=best
print(f"RANSAC vertical VP at ({v[0]:.0f}, {v[1]:.0f}), inliers {inl.sum()}/{len(lines)} (weighted {sc:.0f})")
# refine: weighted least squares on inliers
A=lines[inl]*Ls[inl,None]
_,_,Vt=np.linalg.svd(A); v2=Vt[-1]; v2=v2/v2[2]
print(f"refined vertical VP ({v2[0]:.0f}, {v2[1]:.0f})  -> taper over 1920px = {1920/abs(v2[1])*100:.1f}%")
print(f"  tilt of a true vertical at image centre x=540: {np.degrees(np.arctan((540-v2[0])/(0-v2[1]))):+.2f} deg")
np.save("pullup/work2/vp.npy", v2)
# horizontal reference: the bar
print("bar (measured): -0.38 deg from horizontal")
