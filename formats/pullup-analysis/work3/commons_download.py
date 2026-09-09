"""Download the selected full-resolution Commons originals and write a credits JSON."""
import json, os, re, subprocess, html
UA="DyeAllPies-pullup-video/1.0 (dennisfamiliapedersen@gmail.com)"
PICK={ "spider_monkey":[4,8,9,10,14], "howler_monkey":[2,3,7,11], "capuchin_monkey":[0,5], "squirrel_monkey":[3],
       "marmoset":[0], "golden_lion_tamarin":[1], "mata_atlantica":[0], "rainforest_vertical":[0], "rainforest_canopy":[2] }
creds=[]
for name,idx in PICK.items():
    C=json.load(open(f"pullup/work3/commons/{name}.json"))
    for i in idx:
        c=C[i]; ext=os.path.splitext(c["url"])[1].lower(); fn=f"pullup/assets/commons/{name}_{i:02d}{ext}"
        if not os.path.exists(fn):
            r=subprocess.run(["curl","-sS","-L","-A",UA,"-o",fn,c["url"]],capture_output=True,text=True,timeout=600)
            if r.returncode: print("FAIL",fn,r.stderr[:200]); continue
        artist=html.unescape(re.sub("<[^>]+>","",c["artist"])).strip()
        page="https://commons.wikimedia.org/wiki/"+c["title"].replace(" ","_")
        creds.append(dict(file=fn,title=c["title"],artist=artist,licence=c["lic"],page=page,size=f"{c['w']}x{c['h']}",bytes=os.path.getsize(fn)))
        print(f"{os.path.getsize(fn)/1e6:6.1f} MB  {c['lic']:10s} {artist[:30]:30s} {c['title']}")
json.dump(creds,open("pullup/assets/commons/CREDITS.json","w"),indent=1)
print(len(creds),"files")
