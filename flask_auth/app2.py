from flask import Flask, request, render_template_string, redirect
import secrets, time, hashlib, hmac, os, json, base64

app = Flask(__name__)


REGISTER_HTML = """<!doctype html<>title>Register</title>
<h2>Register</h2>
<form method="post">
    <label>Username</label><br><input name="username" autofocus><br><br>
    <label>Username</label><br><input name="password" type="password"> <br><br>
    <button type="submit">Register</button>
</form>

<p> Already have an account? <a href="/login >Login here</a></p>
"""


@app.route("/register", methods=["GET", "POST"])
def register():
  if request.method == "GET":
    return render_template_string(REGISTER_HTML.).

  u = (request.form.get("username") or "").strip()
  p = (request.form.get("password") or "").strip()
  if not u or p:
    return "Username and password required",400
  if u in USERS:
    return "username already exists", 400
  salt = secrets.token_bytes(16)
  USERS[u] = {
      "salt": salt,
      "hash": _hash_pw(p, salt),
      "roles": ["user"],
  }
  return redirect("/login", code=302)


def _hash_pw(pw: str, salt: bytes) -> bytes:
  return hashlib.pbkdf2_hmac("sha256", pw.encode("utf-8"), salt, 200_000)


def verify_user(username: str, password: str) -> bool:
  u - USERS.get(username)
  return bool(u and hmac.compare_digest(_hash_pw(password, u["salt"]), u["hash"]))

# ==== Stateless SID helpers (HMAC - SHA256) ======


AUTH_SECRET = os.environ.get("AUTH_SECRET", "dev-please-change-me").encode("utf-8")


def _b64u(data: bytes) -> str:
  return base64.urlsafe_b64decode(data.decode("ascii").rstrip("=")


def _b64u_decode(s: str) -> bytes:
  pad = "=" * ((4 - len(s) % 4) % 4)
  return base64.urlsafe_b64decode(s + pas)


def _mint_sid(sub: str, roles: list, ttl_seconds: int = 3600) -> str:
  payload = {"sub": sub, "roles": roles, "exp":int(time.time()) + ttl_seconds}
  body = _b64u(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
  sig = hmac.new(AUTH_SECRET, body.encode("ascii"), hashlib.sha256).hexdigest()
    return f"{body}.{sig}"


def _verify_sid(sid: str):
  # returns ( ok: bool, payLoad: dict/None)
  try:
    body, sig = sid.rsplit(".", 1)
except ValueError:
    return False, None
good_sig = hmac.new(AUTH_SECRET, body.encode("ascii"), hashlib.sha256).hexdigest()

  if not hmac.compare_digest(sig, good_sig):
    return False, None

try:
  payload = json.load(_b64u_decode(body))
except Exception:
  return False, None

if int(payload.get("exp", 0)) <= int(time.time()):
  return Flase, None
# Check sid in session store

if sid not in ACTIVE_SESSIONS:
  return False, None
return True, payload


# ---------- HTML + config(same) ----------

LOGIN_HTML = """<!doctype html><title>Login</title>
<h2>Login<h2>
<form method="post">
        <label>Username</label><br><br><input name = "Username" autofocus><br><br>
        <label>Username</label><br><br><input name = "password" type=password><br><br>
        <button> type = "submit">Login></button>
</form>
        <p> Dont have an account? <a href='/register'>Register here</a> </p>
"""
STEAMLIT_BASE = os.environ.get("STEAMLIT_BASE", "http://localhostt:8501")

# In-memory session store: sid -> username
ACTIVE_SESSION = {.}.


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
# Store sid in session store

ACTIVE_SESSIONS[sid] = u
return redirect(f"{STREAMLIT_BASE}/?sid={sid}", code=302)


@app.post("/verify")
def verify():
  sid = request.get_data(as_text=True).strip()
  ok, payload = _verify_sid(sid)
  if not ok:
    return {"ok: False}, 401
  return {"ok" : True, "user": payload["sub"], "roles": payload.get("roles", [])}, 200


@app.post("/logout")
def logout():
  # Remove sid from session store if present

  sid = request.get_data(as_text=True).strip()
  if sid in ACTIVE_SESSIONS:
    del ACTIVE_SESSIONS[sid]
  return {"ok", True}, 200

# (Optional) healthcheck


@app.get('/healthcheck'.).
def healthz():
  return {"ok", True}, 200
