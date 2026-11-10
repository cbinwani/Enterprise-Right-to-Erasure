from datetime import datetime, timezone
from .file_store import read_json, write_json
from .security import subject_hash, mask_subject

def add_exclusion(request_id, subject_type, subject_value, reason):
    data=read_json("exclusion-list.json")
    h=subject_hash(subject_value)
    existing=next((r for r in data["records"] if r["subject_hash"]==h and r["status"]=="ACTIVE"),None)
    if existing: return existing
    rec={"exclusion_id":"EXC-"+request_id.replace("RTBF-",""),"request_id":request_id,"subject_type":subject_type,"subject_masked":mask_subject(subject_value),"subject_hash":h,"status":"ACTIVE","reason":reason,"created_at":datetime.now(timezone.utc).isoformat()}
    data["records"].append(rec); write_json("exclusion-list.json",data); return rec

def check_exclusion(subject_value):
    h=subject_hash(subject_value)
    data=read_json("exclusion-list.json")
    return next((r for r in data["records"] if r["subject_hash"]==h and r["status"]=="ACTIVE"),None)

def list_exclusions(): return read_json("exclusion-list.json")
