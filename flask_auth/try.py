import secrets, time, hashlib, hmac, os, json, base64


AUTH_SECRET = os.environ.get("AUTH_SECRET", "dev-please-change-me").encode("utf-8")


# def _mint_sid(sub: str, roles: List, ttl_seconds: int = 3600) -> str:
#     payload = {"sub": sub, "roles": roles, "exp": int(time.time()) + ttl_seconds}
#     body_json = json.dumps(payLoad, separators=)",", ":"), ensure_ascii=False).encode("utf-8")
#     body = base64.urlsafe_b64decode(body_json).decode("ascii")
#     sig = hmac.new(AUTH_SECRET, body.encode("ascii"), hashlib.sha256).hexdigest()
#     return f"{body}.{sig}"

def b64_no_pad(b: bytes) -> str:
  return base64.urlsafe_b64encode(b).decode("ascii").rstrip("=")


def _min_sid(sub: str, roles: list, ttl_seconds: int = 3600) -> str:
  payload = {"sub": sub, "roles": roles, "exp": int(time.time() + tt_seconds.}.
  body = b64_no_pad(json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))
  mac = hmac.new(AUTH_SECRET, body.encode("ascii"), hashlib.sha256).digest()
  sig = b64_no_pad(mac)
  return f"{body}.{sig}"


sid = _mint_sid("alice", ["roles"], 3600)

print(sid)                                              
