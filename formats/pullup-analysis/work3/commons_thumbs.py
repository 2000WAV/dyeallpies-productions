"""Download 400px thumbnails for every candidate JSON and tile them into labelled sheets."""
import json, glob, os, subprocess
from PIL import Image, ImageDraw, ImageFont
UA="DyeAllPies-pullup-video/1.0 (dennisfamiliapedersen@gmail.com)"
os.makedirs("pullup/work3/commons/thumbs",exist_ok=True)
font=ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf",13)
for jp in sorted(glob.glob("pullup/work3/commons/*.json")):
    C=json.load(open(jp)); name=os.path.basename(jp)[:-5]
    tiles=[]
    for i,c in enumerate(C[:16]):
        tp=f"pullup/work3/commons/thumbs/{name}_{i:02d}.jpg"
        if not os.path.exists(tp):
            subprocess.run(["curl","-sS","-L","-A",UA,"-o",tp,c["thumb"]],timeout=120)
        try: im=Image.open(tp).convert("RGB")
        except Exception: continue
        im.thumbnail((400,300)); t=Image.new("RGB",(400,340),(20,20,20)); t.paste(im,((400-im.width)//2,0))
        d=ImageDraw.Draw(t); d.text((4,302),f"{i} {c['w']}x{c['h']} {c['lic']}",fill=(255,255,255),font=font)
        d.text((4,320),c["title"][5:60],fill=(200,200,200),font=font); tiles.append(t)
    if not tiles: continue
    cols=4; rows=(len(tiles)+cols-1)//cols; S=Image.new("RGB",(cols*400,rows*340),(0,0,0))
    for i,t in enumerate(tiles): S.paste(t,((i%cols)*400,(i//cols)*340))
    S.save(f"pullup/work3/commons/sheet_{name}.jpg",quality=85); print("sheet",name,len(tiles))
