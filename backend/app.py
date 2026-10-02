"""Flask API and local dashboard server."""
from flask import Flask, jsonify, request, send_from_directory
from threading import Thread, Lock
from urllib.parse import urlparse
import ipaddress, socket, uuid
from pathlib import Path
from .crawler import scan
from .link_checker import check_links
from .form_checker import inspect_forms
from .ai_analyzer import analyze
from .report_generator import generate_report

ROOT=Path(__file__).resolve().parent.parent
app=Flask(__name__,static_folder=str(ROOT/"frontend"),static_url_path="")
JOBS={}; LOCK=Lock()
STATUSES=["Initializing browser...","Crawling pages...","Testing links...","Testing forms...","Checking images...","Detecting JavaScript errors...","Running AI analysis...","Generating report..."]

def validate_url(value):
    p=urlparse(value)
    if p.scheme not in ("http","https") or not p.hostname: raise ValueError("Enter a valid http or https website URL.")
    if p.username or p.password: raise ValueError("URLs containing credentials are not accepted.")
    try: addresses={x[4][0] for x in socket.getaddrinfo(p.hostname,None)}
    except OSError: raise ValueError("The website host could not be resolved.")
    if not addresses or any(not ipaddress.ip_address(a).is_global for a in addresses): raise ValueError("Only publicly reachable websites can be scanned.")
    return value

def run_job(job_id,url):
    job=JOBS[job_id]
    def progress(status,pct):
        if job.get("stop"): raise InterruptedError("Stopped by user")
        job.update(status=status,progress=pct)
    try:
        progress("Initializing browser...",5)
        result=scan(url,progress)
        if job.get("stop"): job.update(status="Stopped",done=True); return
        progress("Testing links...",72)
        same_origin=[x for x in result["links"] if urlparse(x).netloc==urlparse(url).netloc and urlparse(x).scheme==urlparse(url).scheme]
        checked=check_links(same_origin[:100],url)
        broken=[x for x in checked if not x["ok"]]
        for x in broken:
            code=x.get("status")
            result["issues"].append({"url":url,"description":"Broken internal link","category":"Links","severity":"Medium","evidence":f"{x['url']} returned HTTP {code}" if code else f"{x['url']} failed: {x.get('error','request error')}","fix":"Update the destination URL or restore the missing page."})
        progress("Testing forms...",78)
        result["issues"].extend(inspect_forms(result["forms"]))
        progress("Checking images...",83)
        progress("Detecting JavaScript errors...",88)
        if result["capped"]: result["limitations"].append("Page crawl limit reached (20 pages).")
        if len(result["links"])>100: result["limitations"].append("Link check limit reached (100 links).")
        progress("Running AI analysis...",93)
        stats={"pagesTested":len(result["pages"]),"linksTested":len(checked),"formsTested":len(result["forms"]),"imagesTested":len(result["images"]),"javascriptErrors":len(result["jsErrors"]),"brokenLinks":len(broken)}
        summary=analyze(urlparse(url).netloc,stats,result["issues"],result["limitations"])
        progress("Generating report...",98)
        report=generate_report(urlparse(url).netloc,stats,summary,result["issues"])
        job.update(done=True,status="Complete",progress=100,result={"website":urlparse(url).netloc,"stats":stats,"issues":result["issues"],"summary":summary,"report":report,"limitations":result["limitations"],"testedPages":result["pages"]})
    except InterruptedError:
        job.update(done=True,status="Stopped")
    except Exception as exc:
        job.update(done=True,status="Failed",error=str(exc)[:300])

@app.get("/")
def home(): return send_from_directory(ROOT/"frontend","index.html")
@app.post("/api/scan")
def start_scan():
    data=request.get_json(silent=True) or {}
    try: url=validate_url(data.get("url",""))
    except ValueError as e: return jsonify({"error":str(e)}),400
    jid=uuid.uuid4().hex
    with LOCK: JOBS[jid]={"done":False,"status":"Queued","progress":1}
    Thread(target=run_job,args=(jid,url),daemon=True).start()
    return jsonify({"id":jid})
@app.get("/api/scan/<jid>")
def scan_status(jid):
    job=JOBS.get(jid)
    return (jsonify(job),200) if job else (jsonify({"error":"Scan not found"}),404)
@app.post("/api/scan/<jid>/stop")
def stop_scan(jid):
    job=JOBS.get(jid)
    if not job:return jsonify({"error":"Scan not found"}),404
    job["stop"]=True
    return jsonify({"ok":True})

if __name__=="__main__": app.run(host="127.0.0.1",port=5000,debug=False,threaded=True)
