* Flask issues a random **session id (sid)** after login and keeps it in memory.
* Streamlit refuses to render unless it can **POST sid back to Flask** for verification.
* When the user clicks **Logout in Streamlit**, Streamlit **POSTs sid to Flask /logout**, clears its session, and **redirects the browser back to Flask**.

---

# 1) Flask (auth gateway) — `app_auth.py`

```python
# app_auth.py
from flask import Flask, request, render_template_string, redirect
import secrets, time, hashlib, os, hmac

app = Flask(__name__)

# ---- Simple user store with salted PBKDF2 hashes (no extra packages) ----
# Run once to generate a hash for "password123":
# hashlib.pbkdf2_hmac('sha256', b'password123', salt, 200_000)
USERS = {
    "alice": {
        "salt": b"fixed-demo-salt-change-me",
        "hash": bytes.fromhex(
            "e3c9f5b5756cf9f1e4f59f69e201c6b6c7f5f3d2d5b3513a5f4d2f1a9a1f9d7b"
        ),  # <- replace with your own
        "roles": ["user"],
    }
}
def _hash_pw(pw: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", pw.encode("utf-8"), salt, 200_000)

def verify_user(username: str, password: str) -> bool:
    u = USERS.get(username)
    return bool(u and hmac.compare_digest(_hash_pw(password, u["salt"]), u["hash"]))

# ---- Session store (in-memory) ----
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

@app.route("/", methods=["GET"])
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
    # Redirect the browser to Streamlit, carrying the sid once
    return redirect(f"http://localhost:8501/?sid={sid}", code=302)

@app.route("/verify", methods=["POST"])
def verify():
    sid = request.get_data(as_text=True)
    s = SESSIONS.get(sid)
    if not s or s["exp"] <= time.time():
        return {"ok": False}, 401
    return {"ok": True, "user": s["sub"], "roles": s["roles"]}, 200

@app.route("/logout", methods=["POST"])
def logout():
    sid = request.get_data(as_text=True)
    if sid in SESSIONS:
        del SESSIONS[sid]
    return {"ok": True}, 200

if __name__ == "__main__":
    # Local-only by default; adjust host/port as you need
    app.run(port=5000, debug=False)
```

> 🔐 Replace the demo password hash with your own. For each real user, generate a unique `salt` and precompute/store the PBKDF2 hash.

---

# 2) Streamlit (protected app) — `app_streamlit.py`

```python
# app_streamlit.py
import streamlit as st
import urllib.request, urllib.error

FLASK_VERIFY = "http://localhost:5000/verify"
FLASK_LOGOUT = "http://localhost:5000/logout"
FLASK_LOGIN  = "http://localhost:5000/login"

st.set_page_config(page_title="My Protected App", page_icon="🔐")

def _post_text(url: str, data: str, timeout: float = 2.0):
    req = urllib.request.Request(
        url, data=data.encode("utf-8"), method="POST",
        headers={"Content-Type": "text/plain"}
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            import json
            return resp.getcode(), json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, {}
    except Exception:
        return 0, {}

def require_auth():
    # Already authenticated in this Streamlit session?
    if st.session_state.get("user") and st.session_state.get("sid"):
        return

    # Get sid from query params on first load
    qp = st.query_params
    sid = qp.get("sid")
    if isinstance(sid, list):
        sid = sid[0]

    if not sid:
        st.title("🔐 Login required")
        st.write(f"Please sign in at **{FLASK_LOGIN}**.")
        st.stop()

    # Verify with Flask (stdlib urllib only)
    code, payload = _post_text(FLASK_VERIFY, sid)
    if code != 200 or not payload.get("ok"):
        st.error("Session invalid or expired. Please log in again.")
        st.stop()

    # Bind identity to session and scrub URL
    st.session_state.sid = sid
    st.session_state.user = payload["user"]
    st.session_state.roles = payload.get("roles", [])
    st.query_params.clear()

def logout_and_redirect():
    sid = st.session_state.get("sid")
    if sid:
        _post_text(FLASK_LOGOUT, sid)  # best-effort revoke
    st.session_state.clear()
    # Redirect browser back to Flask login (HTML meta refresh; no extra packages)
    st.markdown(
        f'<meta http-equiv="refresh" content="0; url={FLASK_LOGIN}">', 
        unsafe_allow_html=True
    )
    st.stop()

# ---- Gate the app ----
require_auth()

# ---- UI below is protected ----
st.sidebar.write(f"Signed in as **{st.session_state.user}**")
if st.sidebar.button("Log out"):
    logout_and_redirect()

st.title("✅ Protected content")
st.write("This only renders after successful verification with the Flask gateway.")
```

---

## How this satisfies your 5 requirements

1. **Users login from Flask app**: `/login` form validates credentials and creates a server-side session (`sid`).
2. **Directs to Streamlit app**: Flask redirects to `http://localhost:8501/?sid=...`.
3. **User logouts from Streamlit app**: Sidebar “Log out” calls Flask `/logout` with `sid` (revokes the session).
4. **Directs back to Flask**: After logout, Streamlit clears state and issues an immediate HTML meta-refresh to `http://localhost:5000/login`.
5. **No extra packages**: Only Flask + Streamlit + Python stdlib (`hashlib`, `hmac`, `secrets`, `urllib`) are used.

---

## Notes & hardening (still zero extra packages)

* **Short session TTL**: Currently 1 hour; tune `exp` as needed.
* **Per-user salts & strong hashes**: Already using PBKDF2-HMAC-SHA256 with 200k rounds; generate unique salts and store hex hashes.
* **Lock to localhost** (default) during development; for LAN or prod, consider TLS termination via a reverse proxy (still doesn’t change app code).
* **Multipage Streamlit**: Put `require_auth()` at the top of **every page** (e.g., import from a shared `auth_guard.py`).
* **No token leakage**: `sid` is removed from the URL right after first verification (`st.query_params.clear()`).

If you want, tell me your Python version/OS and I’ll give you a tiny helper to generate user salts & password hashes for your `USERS` dict.
