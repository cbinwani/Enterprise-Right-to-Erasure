import hashlib

def subject_hash(value: str) -> str:
    return hashlib.sha256(value.strip().lower().encode()).hexdigest()

def mask_subject(value: str) -> str:
    v=value.strip()
    if "@" in v:
        local, domain=v.split("@",1)
        return (local[:1] + "***@" + domain) if local else "***@"+domain
    return v[:2] + "***" + v[-2:] if len(v)>4 else "***"
