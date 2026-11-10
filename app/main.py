from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from .config import settings
from .file_store import ensure_data, read_json
from .demo_seed import seed
from .models import RTBFRequestIn, IngestionCheck
from .exclusion import list_exclusions, check_exclusion
from .orchestrator import Orchestrator
from .adapters import WebAdapter, GreenAdapter, CotsAdapter
from .system_services import web_app,cots_app,start_legacy_server

app=FastAPI(title="Enterprise RTBF Demonstration Platform",version="3.0.0")
app.mount("/static",StaticFiles(directory="app/static"),name="static")
app.mount("/demo/web",web_app)
app.mount("/demo/cots",cots_app)

@app.on_event("startup")
def startup():
    ensure_data(); seed(); start_legacy_server(); app.state.orchestrator=Orchestrator({"WEB":WebAdapter(),"GREEN_SCREEN":GreenAdapter(),"COTS":CotsAdapter()})

@app.get("/",response_class=HTMLResponse)
def home(): return FileResponse("app/static/index.html")


@app.get("/exclusion",response_class=HTMLResponse)
def exclusion_ui(): return FileResponse("app/static/exclusion.html")

@app.get("/audit",response_class=HTMLResponse)
def audit_ui(): return FileResponse("app/static/audit.html")

@app.get("/validation",response_class=HTMLResponse)
def validation_ui(): return FileResponse("app/static/validation.html")

@app.get("/demo/web",response_class=HTMLResponse)
def demo_web(): return FileResponse("app/static/webapp.html")

@app.get("/demo/cots",response_class=HTMLResponse)
def demo_cots(): return FileResponse("app/static/cots.html")

@app.get("/api/demo/green/search")
def green_demo_search(email:str):
    from .system_services import GREEN
    return [x for x in GREEN if x["email"].lower()==email.lower()]
@app.post("/api/rtbf/requests")
def create(req:RTBFRequestIn):
    rid=app.state.orchestrator.create(req); return {"request_id":rid,"status":"RECEIVED","action":req.action,"exclusion_created":True}
@app.get("/api/rtbf/requests")
def list_requests(): return read_json("requests.json")
@app.get("/api/rtbf/requests/{rid}")
def get_request(rid:str):
    r=app.state.orchestrator.get(rid)
    if not r: raise HTTPException(404,"Request not found")
    return r
@app.get("/api/exclusion-list")
def exclusions(): return list_exclusions()
@app.post("/api/exclusion-list/check")
def exclusion_check(req:IngestionCheck):
    r=check_exclusion(req.subject_value); return {"excluded":bool(r),"record":r}
@app.post("/api/ingestion/decision")
def ingestion(req:IngestionCheck):
    r=check_exclusion(req.subject_value); return {"allowed":not bool(r),"decision":"BLOCK" if r else "ALLOW","reason":r["reason"] if r else "No active exclusion"}
@app.get("/api/audit-log")
def audit_log(): return read_json("audit-log.json")
@app.get("/api/validation/{rid}")
def validation(rid:str):
    r=app.state.orchestrator.get(rid)
    if not r: raise HTTPException(404,"Request not found")
    return {"request_id":rid,"status":r["status"],"action":r["action"],"exclusion":r.get("exclusion"),"systems":r["systems"],"verification":r["verification"],"agent_trace":r["agent_trace"]}
@app.get("/api/agent/architecture")
def agent(): return {"pattern":"Observe -> Plan -> Act -> Verify","mode":"deterministic tool-calling demo agent","tools":["WEB.discover","WEB.delete","WEB.anonymize","GREEN_SCREEN.discover","GREEN_SCREEN.delete","GREEN_SCREEN.anonymize","COTS.discover","COTS.delete","COTS.anonymize"]}
