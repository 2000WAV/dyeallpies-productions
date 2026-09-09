"""Horizontal vanishing point (from the lintel, the bar, the tile grout and the shelves), the
bar line (sub-pixel), the lintel bottom edge, and the jambs, on frames where the bar is clear."""
import cv2, numpy as np, sys
SRC=sys.argv[1]; FR=[int(x) for x in sys.argv[2].split(",")]
cap=cv2.VideoCapture(SRC)
lsd=cv2.createLineSegmentDetector(cv2.LSD_REFINE_ADV)
hsegs=[]; bars=[]; lintels=[]
for fr in FR:
    cap.set(cv2.CAP_PROP_POS_FRAMES, fr); ok,f=cap.read()
    if not ok: print("no frame", fr); continue
    g=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY)
    lines=lsd.detect(g)[0]
    for x1,y1,x2,y2 in lines.reshape(-1,4):
        L=np.hypot(x2-x1,y2-y1)
        if L<120: continue
        ang=np.degrees(np.arctan2(y2-y1, x2-x1)); ang=(ang+90)%180-90
        if abs(ang)<12: hsegs.append((x1,y1,x2,y2,L,ang,fr))
    gb=cv2.GaussianBlur(g,(0,0),1.0).astype(np.float32)
    # bar: dark band; per column find the top edge (bright->dark) and bottom edge (dark->bright) in y 330..430
    pts_top=[]; pts_bot=[]; pts_lin=[]
    for x in range(440, 940, 2):
        col=gb[330:430, x]; d=-np.diff(col); k=int(np.argmax(d))
        if d[k]>25 and 0<k<len(d)-1:
            a,b,c=d[k-1],d[k],d[k+1]; off=(a-c)/(2*(a-2*b+c)+1e-9); pts_top.append((x,330+k+0.5+off))
        d2=np.diff(col); k2=int(np.argmax(d2))
        if d2[k2]>25 and 0<k2<len(d2)-1:
            a,b,c=d2[k2-1],d2[k2],d2[k2+1]; off=(a-c)/(2*(a-2*b+c)+1e-9); pts_bot.append((x,330+k2+0.5+off))
        # lintel bottom edge: in y 250..340 the strongest bright->dark or dark->bright transition
        col2=gb[250:340, x]; d3=np.abs(np.diff(col2)); k3=int(np.argmax(d3))
        if d3[k3]>12: pts_lin.append((x,250+k3+0.5))
    for name,pts,store in (("bar top",pts_top,bars),("bar bottom",pts_bot,None),("lintel",pts_lin,lintels)):
        P=np.array(pts,float)
        if len(P)<20: print(f"frame {fr}: {name}: too few points"); continue
        A=np.polyfit(P[:,0],P[:,1],1); r=P[:,1]-np.polyval(A,P[:,0]); keep=np.abs(r)<2.0
        A=np.polyfit(P[keep,0],P[keep,1],1); r=P[keep,1]-np.polyval(A,P[keep,0])
        print(f"frame {fr}: {name}: y = {A[0]:+.5f} x + {A[1]:.2f}  ({np.degrees(np.arctan(A[0])):+.3f} deg), n={keep.sum()}, resid {r.std():.2f} px, y@x=440 {np.polyval(A,440):.1f} y@x=940 {np.polyval(A,940):.1f}")
        if store is not None: store.append((fr,A,keep.sum(),r.std()))
cap.release()
S=np.array(hsegs,float); print(f"\n{len(S)} long near-horizontal segments; angle median {np.median(S[:,5]):+.2f}")
for band,(y0,y1) in {"top (y<450)":(0,450),"middle":(450,1300),"floor (y>1300)":(1300,1920)}.items():
    m=(S[:,1]>=y0)&(S[:,1]<y1)
    if m.any(): print(f"  {band}: {m.sum()} segs, angle median {np.median(S[m,5]):+.2f}")
lines=[]
for x1,y1,x2,y2,L,a,fr in S:
    l=np.cross([x1,y1,1],[x2,y2,1]); lines.append(l/np.linalg.norm(l[:2]))
lines=np.array(lines); Ls=S[:,4]; best=None; rng=np.random.default_rng(1)
for _ in range(8000):
    i,j=rng.choice(len(lines),2,replace=False); v=np.cross(lines[i],lines[j])
    if abs(v[2])<1e-9: continue
    v=v/v[2]
    if abs(v[0])<1500: continue
    err=np.abs(lines@v)/np.sqrt(v[0]**2+v[1]**2+1e-9); inl=err<3.0; sc=(Ls*inl).sum()
    if best is None or sc>best[0]: best=(sc,v,inl)
sc,v,inl=best; A=lines[inl]*Ls[inl,None]; _,_,Vt=np.linalg.svd(A); v2=Vt[-1]; v2=v2/v2[2]
print(f"horizontal VP RANSAC ({v[0]:.0f},{v[1]:.0f}) inliers {inl.sum()}/{len(lines)}; refined ({v2[0]:.0f},{v2[1]:.0f})")
for y in (380, 960, 1700):
    print(f"  tilt of a true horizontal at y={y}: {np.degrees(np.arctan((y-v2[1])/(v2[0]-540))):+.2f} deg")
np.save("pullup/work3/hvp.npy", v2)
