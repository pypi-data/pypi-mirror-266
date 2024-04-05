import hashlib

def concat(*args: str) -> str:
    ret = ""
    for i in args:
        ret = f"{ret}{i}"
    return ret

def md5(text: str):
    return hashlib.md5(text.encode()).hexdigest()