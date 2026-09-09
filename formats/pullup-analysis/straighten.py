"""Rotate IMG_5990 by -2.70 deg (camera roll, measured from the vertical vanishing point and
cross-checked against the standing and hanging body) with edge replication, no zoom."""
import cv2, numpy as np, subprocess, sys
SRC="IMG_5990.MOV"; OUT="pullup/work2/straight.mp4"; ROLL=2.70
cap=cv2.VideoCapture(SRC)
W=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)); H=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps=cap.get(cv2.CAP_PROP_FPS); N=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
print(f"in {W}x{H} @{fps} {N} frames -> rotate {+ROLL:+.2f} deg (ccw)")
M=cv2.getRotationMatrix2D((W/2,H/2), +ROLL, 1.0)
p=subprocess.Popen(["ffmpeg","-y","-v","error","-f","rawvideo","-pix_fmt","bgr24","-s",f"{W}x{H}",
    "-r",str(fps),"-i","-","-i",SRC,"-map","0:v","-map","1:a?","-c:v","h264_nvenc","-preset","p5",
    "-rc","vbr","-cq","12","-b:v","0","-pix_fmt","yuv420p","-c:a","aac","-b:a","128k",OUT],stdin=subprocess.PIPE)
n=0
while True:
    ok,f=cap.read()
    if not ok: break
    p.stdin.write(cv2.warpAffine(f,M,(W,H),flags=cv2.INTER_LANCZOS4,borderMode=cv2.BORDER_REPLICATE).tobytes()); n+=1
    if n%300==0: print(f"  {n}/{N}", flush=True)
p.stdin.close(); p.wait(); cap.release()
print(f"done {n} frames -> {OUT} (rc {p.returncode})")
