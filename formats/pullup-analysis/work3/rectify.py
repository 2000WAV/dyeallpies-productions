"""Camera model from the two vanishing points, and a metric rectification of the doorway plane.
Assumes square pixels and the principal point at the frame centre. f from the orthogonality of
the vertical and horizontal directions; then R from the VPs; H = K R^-1 K^-1 makes the doorway
plane fronto-parallel (verticals vertical, the bar horizontal). Landmarks are mapped through H
for measurement; the render keeps the original frame."""
import numpy as np, cv2, sys
W,H=1080,1920; cx,cy=W/2,H/2
vv=np.load("pullup/work3/vp.npy"); hv=np.load("pullup/work3/hvp.npy")
f2=-((vv[0]-cx)*(hv[0]-cx)+(vv[1]-cy)*(hv[1]-cy))
print(f"vertical VP {vv[:2].round()}  horizontal VP {hv[:2].round()}  -> f = {np.sqrt(f2):.0f} px (f^2={f2:.3e})")
f=float(np.sqrt(f2)) if f2>0 else 1500.0
K=np.array([[f,0,cx],[0,f,cy],[0,0,1]])
Ki=np.linalg.inv(K)
def dirn(v):
    d=Ki@np.array([v[0],v[1],1.0]); return d/np.linalg.norm(d)
up=dirn(vv); right=dirn(hv)
if up[1]>0: up=-up          # image y grows downward: the vertical VP above the frame is "up"
if right[0]<0: right=-right
# orthogonalise: make 'right' exactly perpendicular to 'up'
right=right-np.dot(right,up)*up; right/=np.linalg.norm(right)
normal=np.cross(right,up)   # the doorway-plane normal
if normal[2]<0: normal=-normal   # must point away from the camera (+z)
print(f"angle between the two VP directions: {np.degrees(np.arccos(abs(np.dot(dirn(vv),dirn(hv))))):.2f} deg (90 = consistent f)")
# camera rotation that maps world axes (right, -up, normal) to camera axes; image y down => world y = -up
R=np.stack([right,-up,normal],axis=1)   # columns = world axes in camera coords
pitch=np.degrees(np.arcsin(-normal[1])); yaw=np.degrees(np.arctan2(normal[0],normal[2])); roll=np.degrees(np.arctan2(right[1],right[0]))
print(f"camera pitch {pitch:+.2f} deg (+ = looking up), yaw {yaw:+.2f} deg, roll {roll:+.2f} deg")
Hm=K@R.T@Ki     # maps the image to the virtual levelled camera
np.save("pullup/work3/H_rect.npy",Hm); np.save("pullup/work3/K.npy",K)
if len(sys.argv)>1:
    cap=cv2.VideoCapture(sys.argv[1]); cap.set(cv2.CAP_PROP_POS_FRAMES,int(sys.argv[2])); ok,fr=cap.read(); cap.release()
    # find the output bounds of the frame corners
    c=np.array([[0,0],[W,0],[W,H],[0,H]],float).reshape(-1,1,2); cw=cv2.perspectiveTransform(c,Hm).reshape(-1,2)
    x0,y0=cw.min(0); x1,y1=cw.max(0); T=np.array([[1,0,-x0],[0,1,-y0],[0,0,1]])
    out=cv2.warpPerspective(fr,T@Hm,(int(x1-x0),int(y1-y0)),flags=cv2.INTER_LINEAR)
    cv2.imwrite(sys.argv[3],out); print("wrote",sys.argv[3],out.shape, "offset",(-x0,-y0))
    # check: bar line endpoints through H
    for x in (440,940):
        y=-0.0334*x+388.0
        p=cv2.perspectiveTransform(np.array([[[x,y]]],float),Hm).reshape(2); print(f"  bar top at x={x}: y={y:.1f} -> rectified {p.round(1)}")
    for x in (440,940):
        y=-0.0372*x+303.0
        p=cv2.perspectiveTransform(np.array([[[x,y]]],float),Hm).reshape(2); print(f"  lintel at x={x}: y={y:.1f} -> rectified {p.round(1)}")
