import uuid, threading
from datetime import datetime, timezone
from .file_store import audit, read_json, write_json
from .exclusion import add_exclusion
from .policy import evaluate

def now(): return datetime.now(timezone.utc).isoformat()

class Orchestrator:
    def __init__(self, adapters): self.adapters=adapters
    def create(self, req):
        rid="RTBF-"+datetime.now().strftime("%Y%m%d")+"-"+uuid.uuid4().hex[:8].upper()
        state={"request_id":rid,"subject_type":req.subject_type,"subject_value":req.subject_value,"action":req.action,"jurisdiction":req.jurisdiction,"reason":req.reason,"status":"RECEIVED","created_at":now(),"updated_at":now(),"systems":[],"verification":[],"agent_trace":[]}
        self._save(state); audit(rid,"privacy-portal","REQUEST_RECEIVED",f"Action={req.action}")
        threading.Thread(target=self.execute,args=(state,),daemon=True).start(); return rid
    def _save(self,state):
        data=read_json("requests.json"); found=False
        for i,x in enumerate(data["records"]):
            if x["request_id"]==state["request_id"]: data["records"][i]=state; found=True; break
        if not found: data["records"].append(state)
        write_json("requests.json",data)
    def get(self,rid): return next((x for x in read_json("requests.json")["records"] if x["request_id"]==rid),None)
    def execute(self,state):
        rid=state["request_id"]
        p=evaluate(state["action"],state["jurisdiction"],state["reason"]); state["status"]=p["status"]; self._save(state); audit(rid,"policy-engine","POLICY_DECISION",p["reason"])
        if not p["eligible"]: return
        ex=add_exclusion(rid,state["subject_type"],state["subject_value"],"RTBF request received"); state["exclusion"]=ex; audit(rid,"exclusion-service","EXCLUSION_CREATED",ex["exclusion_id"])
        state["status"]="EXECUTING"; self._save(state)
        for name,adapter in self.adapters.items():
            entry={"system":name,"action":state["action"],"status":"RUNNING","record_ref":None,"detail":""}; state["systems"].append(entry); self._save(state)
            state["agent_trace"].append({"step":"OBSERVE","system":name,"message":"Discovering subject records"}); self._save(state)
            try:
                records=adapter.discover(state["subject_value"]); state["agent_trace"].append({"step":"PLAN","system":name,"message":f"Found {len(records)} record(s); planned {state['action']}"})
                if records:
                    result=adapter.act(records[0],state["action"]); entry["record_ref"]=records[0]["id"]; entry["status"]="COMPLETED" if result.get("status") in ("DELETED","ANONYMIZED") else "FAILED"; entry["detail"]=str(result)
                else: entry["status"]="COMPLETED"; entry["detail"]="No record found; operation is idempotently complete"
            except Exception as e:
                entry["status"]="FAILED"; entry["detail"]=str(e)
            state["agent_trace"].append({"step":"ACT","system":name,"message":entry["detail"]}); self._save(state); audit(rid,"privacy-agent",f"{name}_{state['action']}",entry["detail"],"SUCCESS" if entry["status"]=="COMPLETED" else "ERROR")
        state["status"]="VERIFYING"; self._save(state)
        verification=[]
        for name,adapter in self.adapters.items():
            try: v=adapter.verify(state["subject_value"])
            except Exception as e: v={"status":"ERROR","detail":str(e)}
            verification.append({"system":name,**v}); state["verification"]=verification; state["agent_trace"].append({"step":"VERIFY","system":name,"message":v["status"]}); self._save(state); audit(rid,"validation-engine",f"{name}_VERIFICATION",v["status"])
        ok=all(v["status"] in ("ABSENT","ANONYMIZED") for v in verification) and all(x["status"]=="COMPLETED" for x in state["systems"])
        state["status"]="COMPLETED" if ok else "PARTIAL_FAILURE"; state["updated_at"]=now(); self._save(state); audit(rid,"validation-engine","REQUEST_COMPLETED",state["status"],"SUCCESS" if ok else "ERROR")
