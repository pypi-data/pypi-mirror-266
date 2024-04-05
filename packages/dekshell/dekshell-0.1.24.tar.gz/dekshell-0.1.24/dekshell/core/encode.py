_prefix = 'shell:'


def encode_run_str(s):
    h = s.encode('utf-8').hex()
    return _prefix + h


def decode_run_str(s):
    if s.startswith(_prefix):
        h = s[len(_prefix):]
        return bytes.fromhex(h).decode('utf-8')
    else:
        return s
