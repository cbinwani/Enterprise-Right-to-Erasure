def evaluate(action,jurisdiction,reason):
    if jurisdiction.upper() not in {"GDPR","CCPA","CPRA","LGPD"}:
        return {"eligible":False,"status":"POLICY_REVIEW","reason":"Jurisdiction requires privacy officer review"}
    if not reason.strip():
        return {"eligible":False,"status":"POLICY_REVIEW","reason":"Reason is required"}
    return {"eligible":True,"status":"APPROVED","reason":f"{jurisdiction} request approved for {action}"}
