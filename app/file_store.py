import json, os, threading
from datetime import datetime, timezone
from .config import settings

_lock=threading.Lock()

def now(): return datetime.now(timezone.utc).isoformat()

def ensure_data():
    os.makedirs(settings.data_dir, exist_ok=True)
    defaults={
      "exclusion-list.json": {"version":"1.0","records":[]},
      "audit-log.json": {"version":"1.0","records":[]}
    }
    for name,obj in defaults.items():
        path=os.path.join(settings.data_dir,name)
        if not os.path.exists(path):
            with open(path,"w",encoding="utf-8") as f: json.dump(obj,f,indent=2)

def read_json(name):
    ensure_data()
    with _lock, open(os.path.join(settings.data_dir,name),encoding="utf-8") as f:
        return json.load(f)

def write_json(name,obj):
    ensure_data()
    tmp=os.path.join(settings.data_dir,name+".tmp")
    with _lock:
        with open(tmp,"w",encoding="utf-8") as f: json.dump(obj,f,indent=2)
        os.replace(tmp,os.path.join(settings.data_dir,name))

def append_json_record(name,record):
    obj=read_json(name); obj.setdefault("records",[]).append(record); write_json(name,obj)

def audit(request_id, actor, event, detail, status="INFO"):
    append_json_record("audit-log.json", {"id":datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f"),"request_id":request_id,"actor":actor,"event":event,"detail":detail,"status":status,"timestamp":now()})
