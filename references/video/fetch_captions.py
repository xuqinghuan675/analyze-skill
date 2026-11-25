"""Read existing YouTube caption tracks only; never download media or run ASR."""
import argparse, concurrent.futures, datetime, json, re, sys
from pathlib import Path
from urllib.parse import urlparse, parse_qs

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/".caption-tools"))
sys.path.insert(0,str(ROOT/".tools"))
if hasattr(sys.stdout,"reconfigure"): sys.stdout.reconfigure(encoding="utf-8")
from youtube_transcript_api import YouTubeTranscriptApi
from requests import Session
import yt_dlp

class BoundedSession(Session):
    def request(self,*args,**kwargs):
        kwargs.setdefault("timeout",12)
        return super().request(*args,**kwargs)

def video_id(value):
    if re.fullmatch(r"[A-Za-z0-9_-]{11}",value): return value
    p=urlparse(value)
    if p.hostname in ("youtu.be","www.youtu.be"):
        value=p.path.strip("/").split("/")[0]
    elif p.hostname in ("www.youtube.com","youtube.com","m.youtube.com"):
        value=parse_qs(p.query).get("v",[""])[0] or p.path.strip("/").split("/")[-1]
    if not re.fullmatch(r"[A-Za-z0-9_-]{11}",value):
        raise ValueError("Expected a YouTube video ID or URL")
    return value

def get_track(vid,langs):
    api=YouTubeTranscriptApi(http_client=BoundedSession())
    tracks=api.list(vid)
    # Manual captions before auto-generated; honor requested language order.
    choices=list(tracks)
    choices=[t for t in choices if any(t.language_code.lower()==l.lower() or t.language_code.lower().startswith(l.lower()+"-") for l in langs)]
    if not choices: raise LookupError("No matching captions: "+str([t.language_code for t in tracks]))
    rank=lambda t: (t.is_generated, next(i for i,l in enumerate(langs) if t.language_code.lower()==l.lower() or t.language_code.lower().startswith(l.lower()+"-")))
    t=min(choices,key=rank); data=t.fetch().to_raw_data()
    if not data: raise ValueError("Empty caption track")
    return data, {"language":t.language_code,"generated":t.is_generated,"extractor":"youtube-transcript-api"}

def get_yt_dlp(vid,langs):
    opts={"quiet":True,"no_warnings":True,"skip_download":True,"socket_timeout":10,"retries":0,"extractor_retries":0,"noplaylist":True}
    with yt_dlp.YoutubeDL(opts) as y:
        d=y.extract_info("https://www.youtube.com/watch?v="+vid,download=False)
        for group,generated in (("subtitles",False),("automatic_captions",True)):
            tracks=d.get(group) or {}
            for lang in langs:
                for code,formats in tracks.items():
                    if code.lower()!=lang.lower() and not code.lower().startswith(lang.lower()+"-"): continue
                    f=next((f for f in formats if f.get("ext")=="json3" and f.get("url")),None)
                    if not f: continue
                    try:
                        with y.urlopen(f["url"]) as resp: raw=json.loads(resp.read())
                        data=[]
                        for e in raw.get("events",[]):
                            t="".join(s.get("utf8","") for s in e.get("segs",[])).strip()
                            if t:data.append({"text":t,"start":e.get("tStartMs",0)/1000,"duration":e.get("dDurationMs",0)/1000})
                        if data:return data,{"language":code,"generated":generated,"extractor":"yt-dlp"}
                    except Exception: continue
        raise LookupError("No retrievable matching caption track")

def collect(vid,output,langs):
    p=output/vid;p.mkdir(parents=True,exist_ok=True)
    if (p/"captions.json").exists():
        d=json.loads((p/"captions.json").read_text(encoding="utf-8"))
        if d.get("snippets"):return {"id":vid,"status":"cached","count":len(d["snippets"])}
    errors=[]
    for getter in (get_track,get_yt_dlp):
        try:
            data,meta=getter(vid,langs)
            payload={"video_id":vid,"url":"https://www.youtube.com/watch?v="+vid,"retrieved_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),**meta,"snippets":data}
            (p/"captions.json").write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
            (p/"transcript.txt").write_text("\n".join(f"[{s['start']:.2f}] {s['text']}" for s in data),encoding="utf-8")
            return {"id":vid,"status":"ok","count":len(data),"last_timestamp":data[-1]["start"],**meta}
        except Exception as e:errors.append({"extractor":getter.__name__,"type":type(e).__name__,"message":str(e)[:400]})
    result={"id":vid,"status":"unavailable","errors":errors}
    (p/"status.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    return result

if __name__=="__main__":
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument("videos",nargs="+");a.add_argument("--languages",nargs="+",default=["zh","zh-Hans","zh-Hant","zh-CN","zh-TW"])
    a.add_argument("--workers",type=int,default=2)
    args=a.parse_args()
    ids=list(dict.fromkeys(video_id(v) for v in args.videos))
    out=ROOT/"references"/"video"/"captions"
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1,min(args.workers,3))) as pool:
        results=[]
        for f in concurrent.futures.as_completed([pool.submit(collect,v,out,args.languages) for v in ids]):
            r=f.result();results.append(r);print(json.dumps(r,ensure_ascii=False),flush=True)
    (out/"latest_run.json").write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding="utf-8")
