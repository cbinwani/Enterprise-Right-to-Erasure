from app.security import subject_hash,mask_subject

def test_hash_normalized(): assert subject_hash(' Alice@Example.com ') == subject_hash('alice@example.com')
def test_mask(): assert mask_subject('alice@example.com').startswith('a***@')
