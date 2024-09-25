def code_secret_key(key):
    return f"PB{int(key)*2024}"


def decode_secret_key(key):
    return int(key/2024)
