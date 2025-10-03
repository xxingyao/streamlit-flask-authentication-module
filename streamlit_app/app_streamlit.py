from flask import Flask, request, render_template_string, redirect
import secrets, time, hashlib, hmac, os, json, base64

app = Flask(__name__)

# ----- Demo user store (same as before) -----
USERS = {
    "alice": {
        "salt": b"fixed-demo-salt-change-me",
        "hash": bytes.fromhex("4912b210bcaff3909b93a22e3de1f4c1a4eebe5b30908bc4718952b24465380f"),
        "roles": ["user"],
    }
}

def _hash_pw(pw: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", pw.encode("utf-8"), salt, 200_000)

def verify_user(username: str, password: str) -> bool:
    u = USERS.get(username)
    return bool(u and hmac.compare_digest(_hash_pw(password, u["salt"]), u["hash"]))

# ===== Stateless SID helpers (HMAC-SHA256) =====
AUTH_SECRET = os.environ.get("AUTH_SECRET", "dev-please-change-me").encode("utf-8")

def _b64u(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")

def _b64u_decode(s: str) -> bytes:
    pad = "=" * ((4 - len(s) % 4) % 4)
    return base64.urlsafe_b64decode(s + pad)

def _mint_sid(sub: str, roles: list, ttl_seconds: int = 3600) -> str:
    payload = {"sub": sub, "roles": roles, "exp": int(time.time()) + ttl_seconds}
    body = _b64u(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    sig = hmac.new(AUTH_SECRET, body.encode("ascii"), hashlib.sha256).hexdigest()
    return f"{body}.{sig}"

def _verify_sid(sid: str):
    # returns (ok: bool, payload: dict|None)
    try:
        body, sig = sid.rsplit(".", 1)
    except ValueError:
        return False, None
    good_sig = hmac.new(AUTH_SECRET, body.encode("ascii"), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(sig, good_sig):
        return False, None
    try:
        payload = json.loads(_b64u_decode(body))
    except Exception:
        return False, None
    if int(payload.get("exp", 0)) <= int(time.time()):
        return False, None
    return True, payload

# ----- HTML + config (same) -----
LOGIN_HTML = """<!doctype html><title>Login</title>
<h2>Login</h2>
<form method="post">
  <label>Username</label><br><input name="username" autofocus><br><br>
  <label>Password</label><br><input name="password" type="password"><br><br>
  <button type="submit">Login</button>
</form>"""

STREAMLIT_BASE = os.environ.get("STREAMLIT_BASE", "http://localhost:8501")

@app.get("/")
def index():
    return redirect("/login", code=302)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template_string(LOGIN_HTML)

    u = (request.form.get("username") or "").strip()
    p = (request.form.get("password") or "").strip()

    if not verify_user(u, p):
        return "Invalid credentials", 401

    roles = USERS[u]["roles"]
    sid = _mint_sid(u, roles, ttl_seconds=3600)
    return redirect(f"{STREAMLIT_BASE}/?sid={sid}", code=302)

@app.post("/verify")
def verify():
    sid = request.get_data(as_text=True).strip()
    ok, payload = _verify_sid(sid)
    if not ok:
        return {"ok": False}, 401
    return {"ok": True, "user": payload["sub"], "roles": payload.get("roles", [])}, 200

@app.post("/logout")
def logout():
    # Stateless tokens can't be truly revoked without a denylist/DB; treat as best-effort success.
    return {"ok": True}, 200

# (Optional) healthcheck
@app.get("/healthz")
def healthz():
    return {"ok": True}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
