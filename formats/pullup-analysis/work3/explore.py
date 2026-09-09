import numpy as np, cv2, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.signal import savgol_filter, find_peaks
d=np.load("pullup/work3/pose_mp.npz"); img=d["img"]; ok=d["ok"]; fps=float(d["fps"]); W=int(d["width"]); H=int(d["height"])
P=img[:,:,:2]*np.array([W,H]); V=img[:,:,3]; N=len(P); t=np.arange(N)/fps
def interp(a):
    a=np.array(a,float); m=np.isfinite(a)
    if not m.all(): a[~m]=np.interp(np.arange(len(a))[~m],np.arange(len(a))[m],a[m])
    return a
for j in range(P.shape[1]):
    for c in range(2): P[:,j,c]=interp(P[:,j,c])
V=np.nan_to_num(V)
sh=(P[:,11]+P[:,12])/2; ank=(P[:,27]+P[:,28])/2; wr=(P[:,15]+P[:,16])/2
sh_y=savgol_filter(sh[:,1],9,2); hands_up=(P[:,15,1]<P[:,11,1])&(P[:,16,1]<P[:,12,1])&ok
idx=np.where(hands_up)[0]; print("hands-up frames", idx[0], idx[-1], f"{idx[0]/fps:.1f}-{idx[-1]/fps:.1f} s", "ok frames", ok.sum())
tops,_=find_peaks(-sh_y[idx[0]:idx[-1]],prominence=0.05*H,distance=int(0.6*fps)); tops+=idx[0]
print("tops:", len(tops), [f"{x/fps:.1f}" for x in tops])
print("sh_y at tops:", [int(sh_y[x]) for x in tops]); 
fig,ax=plt.subplots(4,1,figsize=(16,12),sharex=True)
ax[0].plot(t,sh_y); ax[0].plot(t[tops],sh_y[tops],"rv"); ax[0].invert_yaxis(); ax[0].set_ylabel("shoulder y")
ax[1].plot(t,ank[:,1]); ax[1].plot(t,V[:,27]*1900,alpha=.3); ax[1].invert_yaxis(); ax[1].set_ylabel("ankle y (+vis)")
ax[2].plot(t,V[:,0],label="nose vis"); ax[2].plot(t,V[:,7],label="ear vis"); ax[2].plot(t,ok*1.0,label="ok"); ax[2].legend()
ax[3].plot(t,P[:,0,1],label="nose y"); ax[3].plot(t,wr[:,1],label="wrist y"); ax[3].axhline(365,color="k"); ax[3].invert_yaxis(); ax[3].legend()
plt.tight_layout(); plt.savefig("pullup/work3/explore.png",dpi=80)
cap=cv2.VideoCapture("pullup/work3/master.mp4"); crops=[]
for f in tops:
    cap.set(cv2.CAP_PROP_POS_FRAMES,int(f)); okf,fr=cap.read()
    c=fr[150:650,380:1000].copy(); cv2.putText(c,f"{f/fps:.1f}s",(10,40),cv2.FONT_HERSHEY_SIMPLEX,1.2,(0,0,255),3); crops.append(cv2.resize(c,(310,250)))
rows=[np.hstack(crops[i:i+7]) for i in range(0,len(crops),7)]; rows=[r if r.shape[1]==rows[0].shape[1] else np.hstack([r,np.zeros((250,rows[0].shape[1]-r.shape[1],3),np.uint8)]) for r in rows]
cv2.imwrite("pullup/work3/tops_strip.jpg",np.vstack(rows))
