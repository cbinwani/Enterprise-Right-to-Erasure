from app.security import subject_hash
from app.exclusion import add_exclusion,check_exclusion

def test_exclusion(tmp_path,monkeypatch):
    from app.config import settings
    monkeypatch.setattr(settings,'data_dir',str(tmp_path));
    from app.file_store import ensure_data
    ensure_data(); add_exclusion('RTBF-1','EMAIL','alice@example.com','RTBF request received')
    r=check_exclusion('ALICE@example.com'); assert r and r['status']=='ACTIVE'
