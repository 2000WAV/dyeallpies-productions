"""Re-query the API for the full Artist / Credit / LicenseUrl of every downloaded file."""
import json, urllib.parse, subprocess, re, html
UA="DyeAllPies-pullup-video/1.0 (dennisfamiliapedersen@gmail.com)"
creds=json.load(open("pullup/assets/commons/CREDITS.json"))
titles="|".join(c["title"] for c in creds)
url="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode(dict(action="query",format="json",titles=titles,prop="imageinfo",iiprop="extmetadata",iiextmetadatafilter="Artist|Credit|LicenseShortName|LicenseUrl|Attribution|AttributionRequired"))
res=json.loads(subprocess.run(["curl","-sS","-L","-A",UA,url],capture_output=True,text=True,timeout=120).stdout)
by={p["title"]:p["imageinfo"][0]["extmetadata"] for p in res["query"]["pages"].values() if "imageinfo" in p}
strip=lambda s: html.unescape(re.sub("<[^>]+>","",s)).strip()
for c in creds:
    em=by.get(c["title"],{})
    c["artist"]=strip(em.get("Artist",{}).get("value",c["artist"]))
    c["credit"]=strip(em.get("Credit",{}).get("value",""))
    c["licence"]=em.get("LicenseShortName",{}).get("value",c["licence"]); c["licence_url"]=em.get("LicenseUrl",{}).get("value","")
    c["attribution_required"]=em.get("AttributionRequired",{}).get("value","")
    print(f"{c['licence']:10s} req={c['attribution_required']:5s} {c['artist'][:40]:40s} | {c['credit'][:50]:50s} | {c['file']}")
json.dump(creds,open("pullup/assets/commons/CREDITS.json","w"),indent=1,ensure_ascii=False)
