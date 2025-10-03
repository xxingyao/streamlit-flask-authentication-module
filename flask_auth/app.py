from flask import Flask, request, render_template_string, redirect
import secrets, time, hashlib, hmac, os

app = Flask(__name__)

# ----- Simple user store (demo only) -----
# Generate your own salt + hash for real use.
USERS = {
    "alice": {
        "salt": b"fixed-demo-salt-change-me",
        "hash": bytes.fromhex(
            "e3c9f5b5756cf9f1e4f59f69e201c6b6c7f5f3d2d5b3513a5f4d2f1a9a1f9d7b"
        ),
        "roles": ["user"],
    }
}

def _hash_pw(pw: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", pw.encode("utf-8"), salt, 200_000)

def verify_user(username: str, password: str) -> bool:
    u = USERS.get(username)
    return bool(u and hmac.compare_digest(_hash_pw(password, u["salt"]), u["hash"]))

# ----- Session store (in-memory) -----
SESSIONS = {}  # sid -> {"sub": "...", "roles": [...], "exp": <unix>}

LOGIN_HTML = """
<!doctype html>
<title>Login</title>
<h2>Login</h2>
<form method="post">
  <label>Username</label><br><input name="username" autofocus><br><br>
  <label>Password</label><br><input name="password" type="password"><br><br>
  <button type="submit">Login</button>
</form>
"""

# Where to send the browser after successful login (Streamlit base, no trailing slash)
STREAMLIT_BASE = os.environ.get("STREAMLIT_BASE", "http://localhost:8501")

@app.get("/")
def index():
    return redirect("/login", code=302)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template_string(LOGIN_HTML)

    u = (request.form.get("username") or "").strip()
    p = request.form.get("password") or ""

    if not verify_user(u, p):
        return "Invalid credentials", 401

    sid = secrets.token_urlsafe(32)
    SESSIONS[sid] = {"sub": u, "roles": USERS[u]["roles"], "exp": time.time() + 3600}

    # Redirect to Streamlit with the one-time sid
    return redirect(f"{STREAMLIT_BASE}/?sid={sid}", code=302)

@app.post("/verify")
def verify():
    sid = request.get_data(as_text=True)
    s = SESSIONS.get(sid)
    if not s or s["exp"] <= time.time():
        return {"ok": False}, 401
    return {"ok": True, "user": s["sub"], "roles": s["roles"]}, 200

@app.post("/logout")
def logout():
    sid = request.get_data(as_text=True)
    if sid in SESSIONS:
        del SESSIONS[sid]
    return {"ok": True}, 200

if __name__ == "__main__":
    # Local dev
    app.run(host="0.0.0.0", port=5000, debug=True)
