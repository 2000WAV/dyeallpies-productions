"""Search Wikimedia Commons for large, permissively licensed photos. Prints candidates and
saves a JSON. Usage: commons_search.py "query" out.json [min_width=2500] [limit=40]"""
import sys, json, urllib.parse, subprocess
q=sys.argv[1]; out=sys.argv[2]; minw=int(sys.argv[3]) if len(sys.argv)>3 else 2500; lim=int(sys.argv[4]) if len(sys.argv)>4 else 40
UA={"User-Agent":"DyeAllPies-pullup-video/1.0 (dennisfamiliapedersen@gmail.com) python-urllib"}
def get(params):
    url="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode(params)
    r=subprocess.run(["curl","-sS","-L","-A",UA["User-Agent"],url],capture_output=True,text=True,timeout=90)
    return json.loads(r.stdout)
OK=("cc0","cc by 2.0","cc by 2.5","cc by 3.0","cc by 4.0","public domain","pd")
res=get(dict(action="query",format="json",generator="search",gsrsearch=f"filetype:bitmap {q}",gsrnamespace=6,gsrlimit=lim,
             prop="imageinfo",iiprop="url|size|extmetadata",iiurlwidth=400,iiextmetadatafilter="LicenseShortName|Artist|ImageDescription|Credit"))
cands=[]
for p in res.get("query",{}).get("pages",{}).values():
    ii=p["imageinfo"][0]; em=ii.get("extmetadata",{})
    lic=em.get("LicenseShortName",{}).get("value","?"); w,h=ii["width"],ii["height"]
    ok=lic.lower().replace("-"," ") in OK or lic.lower().startswith("cc0") or "public domain" in lic.lower()
    if w<minw or not ok: continue
    u=ii["url"].split("?")[0]; thumb=ii.get("thumburl",u).split("?")[0]
    cands.append(dict(title=p["title"],w=w,h=h,lic=lic,artist=em.get("Artist",{}).get("value","?")[:80],url=u,thumb=thumb))
cands.sort(key=lambda c:-c["w"]*c["h"])
for c in cands: print(f"{c['w']}x{c['h']}  {c['lic']:12s}  {c['title']}")
json.dump(cands,open(out,"w"),indent=1)
print(f"{len(cands)} candidates -> {out}")
