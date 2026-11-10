import threading, socket
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from .config import settings
from .file_store import now

web_app=FastAPI(title="Demo Modern Web Application")
cots_app=FastAPI(title="Demo COTS CRM")

@web_app.get("/", response_class=HTMLResponse)
def web_home():
    return "<html><head><title>Sample Modern Web Application</title></head><body style=\"font-family:Arial;margin:40px\"><h1>Sample Modern Web Application</h1><p>Demo customer system. RTBF target.</p><pre id=\"data\">Loading...</pre><script>async function load(){document.getElementById(\"data\").textContent=JSON.stringify(await (await fetch(\"/api/customers\")).json(),null,2)}load();setInterval(load,2000)</script></body></html>"

@cots_app.get("/", response_class=HTMLResponse)
def cots_home():
    return "<html><head><title>Sample COTS CRM</title></head><body style=\"font-family:Arial;margin:40px\"><h1>Sample COTS CRM</h1><p>Vendor-style demo application with a privacy endpoint.</p><pre id=\"data\">Loading...</pre><script>async function load(){document.getElementById(\"data\").textContent=JSON.stringify(await (await fetch(\"/api/v1/contacts\")).json(),null,2)}load();setInterval(load,2000)</script></body></html>"

WEB=[{"id":"WEB-1001","email":"alice@example.com","name":"Alice Johnson","phone":"555-0101","status":"ACTIVE"},{"id":"WEB-1002","email":"bob@example.com","name":"Bob Smith","phone":"555-0102","status":"ACTIVE"}]
COTS=[{"id":"COT-4422","email":"alice@example.com","name":"Alice Johnson","phone":"555-0101","status":"ACTIVE"},{"id":"COT-9911","email":"bob@example.com","name":"Bob Smith","phone":"555-0102","status":"ACTIVE"}]
GREEN=[{"id":"GRN-7788","email":"alice@example.com","name":"ALICE JOHNSON","phone":"5550101","status":"ACTIVE"},{"id":"GRN-9911","email":"bob@example.com","name":"BOB SMITH","phone":"5550102","status":"ACTIVE"}]

@web_app.get("/api/customers")
def web_customers(): return WEB
@web_app.get("/api/customers/search")
def web_search(email:str): return [x for x in WEB if x["email"].lower()==email.lower()]
@web_app.delete("/api/customers/{cid}")
def web_delete(cid:str):
    for i,x in enumerate(WEB):
        if x["id"]==cid: WEB.pop(i); return {"status":"DELETED","id":cid,"timestamp":now()}
    raise HTTPException(404,"not found")
@web_app.patch("/api/customers/{cid}/anonymize")
def web_anonymize(cid:str):
    for x in WEB:
        if x["id"]==cid: x.update(email="erased@invalid.local",name="ANONYMIZED",phone="0000000000",status="ANONYMIZED"); return {"status":"ANONYMIZED","id":cid,"timestamp":now()}
    raise HTTPException(404,"not found")

@cots_app.get("/api/v1/contacts")
def cots_contacts(): return {"records":COTS}
@cots_app.get("/api/v1/contacts/search")
def cots_search(email:str): return {"records":[x for x in COTS if x["email"].lower()==email.lower()]}
@cots_app.post("/api/v1/privacy/execute")
def cots_execute(payload:dict):
    cid=payload.get("contactId"); action=payload.get("action","DELETE")
    for i,x in enumerate(COTS):
        if x["id"]==cid:
            if action=="DELETE": COTS.pop(i); return {"status":"DELETED","contactId":cid,"timestamp":now()}
            x.update(email="erased@invalid.local",name="ANONYMIZED",phone="0000000000",status="ANONYMIZED"); return {"status":"ANONYMIZED","contactId":cid,"timestamp":now()}
    return {"status":"NOT_FOUND","contactId":cid}

def green_server():
    s=socket.socket(); s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1); s.bind((settings.host,settings.green_port)); s.listen(20)
    while True:
        conn,_=s.accept()
        try:
            conn.sendall(b"LEGACY GREEN SCREEN CUSTOMER SYSTEM\nLOGIN: "); conn.recv(1024); conn.sendall(b"PASSWORD: "); conn.recv(1024)
            conn.sendall(b"\nMENU: S=SEARCH D=DELETE A=ANONYMIZE Q=QUIT\n> ")
            while True:
                cmd=conn.recv(1024).decode(errors="ignore").strip().upper()
                if cmd=="S":
                    conn.sendall(b"EMAIL: "); email=conn.recv(1024).decode().strip()
                    row=next((x for x in GREEN if x["email"].lower()==email.lower()),None)
                    conn.sendall((f"FOUND|{row['id']}|{row['email']}|{row['name']}|{row['status']}\n> " if row else "NOT FOUND\n> ").encode())
                elif cmd in ("D","A"):
                    conn.sendall(b"CUSTOMER ID: "); cid=conn.recv(1024).decode().strip(); row=next((x for x in GREEN if x["id"]==cid),None)
                    if not row: conn.sendall(b"NOT FOUND\n> "); continue
                    if cmd=="D": GREEN.remove(row); msg="DELETED"
                    else: row.update(email="erased@invalid.local",name="ANONYMIZED",phone="0000000000",status="ANONYMIZED"); msg="ANONYMIZED"
                    conn.sendall((msg+"\n> ").encode())
                elif cmd=="Q": break
                else: conn.sendall(b"INVALID\n> ")
        finally:
            conn.close()

def start_legacy_server():
    threading.Thread(target=green_server,daemon=True,name="green-screen").start()
    import uvicorn
    threading.Thread(target=lambda: uvicorn.run(web_app,host=settings.host,port=settings.web_port,log_level="warning"),daemon=True,name="web-app").start()
    threading.Thread(target=lambda: uvicorn.run(cots_app,host=settings.host,port=settings.cots_port,log_level="warning"),daemon=True,name="cots-app").start()
