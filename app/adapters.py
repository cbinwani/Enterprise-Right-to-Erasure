import socket, httpx
from .config import settings

class WebAdapter:
    def __init__(self): self.base=f"http://{settings.host}:{settings.web_port}"
    def discover(self,email): return httpx.get(self.base+"/api/customers/search",params={"email":email}).json()
    def act(self,record,action):
        if action=="DELETE": return httpx.delete(self.base+f"/api/customers/{record['id']}").json()
        return httpx.patch(self.base+f"/api/customers/{record['id']}/anonymize").json()
    def verify(self,email):
        rows=self.discover(email); return {"status":"ABSENT" if not rows else ("ANONYMIZED" if rows[0]["status"]=="ANONYMIZED" else "PRESENT"),"records":rows}

class CotsAdapter:
    def __init__(self): self.base=f"http://{settings.host}:{settings.cots_port}"
    def discover(self,email): return httpx.get(self.base+"/api/v1/contacts/search",params={"email":email}).json()["records"]
    def act(self,record,action): return httpx.post(self.base+"/api/v1/privacy/execute",json={"contactId":record["id"],"action":action}).json()
    def verify(self,email):
        rows=self.discover(email); return {"status":"ABSENT" if not rows else ("ANONYMIZED" if rows[0]["status"]=="ANONYMIZED" else "PRESENT"),"records":rows}

class GreenAdapter:
    def __init__(self): self.host=settings.host; self.port=settings.green_port
    def _session(self):
        s=socket.create_connection((self.host,self.port),timeout=5); s.recv(4096); s.sendall(b"privacy-agent\n"); s.recv(4096); s.sendall(b"demo-password\n"); s.recv(4096); return s
    def discover(self,email):
        s=self._session(); s.sendall(b"S\n"); s.recv(1024); s.sendall((email+"\n").encode()); out=s.recv(4096).decode(); s.sendall(b"Q\n"); s.close()
        if "FOUND|" not in out: return []
        p=out.split("FOUND|",1)[1].split("\n",1)[0].split("|"); return [{"id":p[0],"email":p[1],"name":p[2],"status":p[3]}]
    def act(self,record,action):
        s=self._session(); s.sendall(("D\n" if action=="DELETE" else "A\n").encode()); s.recv(1024); s.sendall((record["id"]+"\n").encode()); out=s.recv(4096).decode(); s.sendall(b"Q\n"); s.close(); return {"status":"DELETED" if "DELETED" in out else ("ANONYMIZED" if "ANONYMIZED" in out else "FAILED"),"id":record["id"]}
    def verify(self,email):
        rows=self.discover(email); return {"status":"ABSENT" if not rows else ("ANONYMIZED" if rows[0]["status"]=="ANONYMIZED" else "PRESENT"),"records":rows}
