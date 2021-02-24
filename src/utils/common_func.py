import hashlib


def compute_md5(content: str, salt: str = None) -> str:
    m = hashlib.md5()
    m.update(content.encode('utf-8'))
    if salt is not None:
        m.update(salt.encode('utf-8'))
    return m.hexdigest()
