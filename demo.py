import time, httpx
base='http://127.0.0.1:8000'
print('Submit a request from the browser at http://127.0.0.1:8000')
print('API example:')
r=httpx.post(base+'/api/rtbf/requests',json={'subject_type':'EMAIL','subject_value':'alice@example.com','action':'DELETE','jurisdiction':'GDPR','reason':'Customer request'})
print(r.json()); rid=r.json()['request_id']
while True:
    d=httpx.get(base+'/api/rtbf/requests/'+rid).json(); print(d['status'])
    if d['status'] in ('COMPLETED','PARTIAL_FAILURE','POLICY_REVIEW'): print(d); break
    time.sleep(1)
