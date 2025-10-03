# Flask ↔ Streamlit Auth Gateway (stdlib-only)

Protect a Streamlit app behind a simple Flask login **without any extra packages** beyond Flask, Streamlit, and the Python standard library.

**Flow**
1. User logs in at `http://localhost:5000/login` (Flask).
2. Flask verifies credentials, creates a server-side session (`sid`), and redirects to `http://localhost:8501/?sid=...` (Streamlit).
3. Streamlit verifies the `sid` by POSTing it back to Flask (`/verify`) using `urllib.request`.
4. User clicks **Log out** in Streamlit → Streamlit revokes the session via Flask (`/logout`) and sends the browser back to Flask’s login.

---

## Repo contents

- `app_auth.py` — Flask app: login form, in-memory user store (PBKDF2), session issuance, `/verify`, `/logout`.
- `app_streamlit.py` — Streamlit app: hard gate with `require_auth()`, logout button, redirect back to Flask.
- *(Optional)* `helpers/` — snippets you may add later (password hash generator, etc.).

---

## Prerequisites

- Python 3.8+ recommended
- Flask and Streamlit installed (no other packages)
  ```bash
  pip install flask streamlit
  ```

---

## Quick start

Open two terminals in the project directory.

**Terminal A — Flask**
```bash
python app_auth.py
```

**Terminal B — Streamlit**
```bash
streamlit run app_streamlit.py --server.headless=true --server.port=8501
```

Visit: **`http://localhost:5000/login`**  
Log in → you’ll be redirected to the protected Streamlit app.

---

## Configuration

### Ports & URLs
- Default Flask: `http://localhost:5000`
- Default Streamlit: `http://localhost:8501`
- If you change ports, update the constants at the top of `app_streamlit.py`:
  ```python
  FLASK_VERIFY = "http://localhost:5000/verify"
  FLASK_LOGOUT = "http://localhost:5000/logout"
  FLASK_LOGIN  = "http://localhost:5000/login"
  ```

### Session lifetime
- Sessions expire after **1 hour** by default. Change when creating the session in `app_auth.py`:
  ```python
  SESSIONS[sid] = {"sub": u, "roles": USERS[u]["roles"], "exp": time.time() + 3600}
  ```

### Multipage Streamlit apps
- Call `require_auth()` at the **top of every page** (import it into each file) to ensure nothing renders without authentication.

---

## Adding users (no plaintext passwords)

Users live in the in-memory `USERS` dict inside `app_auth.py`. Each user needs:
- a unique **salt** (`bytes`)
- a PBKDF2-HMAC-SHA256 **hash** (hex string)
- optional **roles** (list)

**Generate a password hash (one-liner in Python):**
```python
import hashlib
salt = b"my-unique-salt-123"            # choose a unique salt per user
pw   = b"password123"                   # the user's chosen password
print(hashlib.pbkdf2_hmac("sha256", pw, salt, 200_000).hex())
```

**Add to `USERS`:**
```python
USERS = {
  "alice": {
    "salt": b"my-unique-salt-123",
    "hash": "<hex-from-generator>",
    "roles": ["user"]  # or ["admin", "user"]
  }
}
```

> Tip: Store users in a file/DB for persistence if you restart the Flask process often.

---

## How the guard works (high level)

- **On first load**, Streamlit looks for `sid` in `st.query_params`.
- If missing → show “Login required” and `st.stop()`.
- If present → Streamlit **POSTs** the `sid` to Flask `/verify` using `urllib.request`.
- If valid → bind `user`, `roles`, and `sid` into `st.session_state`, **clear the URL query** (`st.query_params.clear()`), and render the app.
- **Logout** button calls Flask `/logout` with the `sid`, clears Streamlit session state, and meta-refreshes the browser back to Flask `/login`.

---

## Security notes (still zero extra packages)

- **No plaintext passwords**: PBKDF2-HMAC-SHA256 with 200k iterations (adjust as needed).
- **Per-user salts** are required; never reuse the same salt across all users.
- **Short session TTL** and revoke on logout.
- **Scrub query tokens**: we remove `sid` from the URL right after verification (prevents log/history leakage).
- **Local-only** by default. For intranet/production, front with a reverse proxy (Nginx/Traefik/Apache) and TLS termination.
- **Least privilege UI**: gate admin functions via the `roles` claim in `st.session_state`.

---

## Troubleshooting

- **I can hit `:8501` without logging in.**  
  Ensure `require_auth()` is called at the *very top* of every Streamlit page before any content or expensive data loads.

- **“Session invalid or expired.”**  
  The `sid` isn’t in Flask’s memory (expired or Flask restarted). Log in again.

- **CORS issues?**  
  We post from `http://localhost:8501` to `http://localhost:5000`. Browsers allow this simple POST without custom headers; if you add custom headers, you may need CORS handling.

- **After logout I’m still seeing the app.**  
  The Streamlit page meta-refreshes back to Flask immediately, but if you navigate back, the guard should block and ask you to log in again.

---

## FAQ

**Why not JWT / `itsdangerous`?**  
To meet a strict “no extra packages” requirement and enable easy server-side session revocation. If you later want stateless tokens, you can switch to HMAC or `itsdangerous` with minimal code changes.

**Can I avoid the `sid` in the URL altogether?**  
Use a reverse proxy and set an HTTP-only cookie from Flask, then have Streamlit read/verify it. That’s a small infra change, not a code change in principle.

**Will this work offline?**  
Yes. No dependency on external services; only Flask ↔ Streamlit over localhost.

---

## Next steps (optional enhancements)

- Persist sessions to a file/DB instead of memory.
- Add “remember me” (longer TTL) vs “strict” (short TTL).
- Role-based menus and route guards inside Streamlit.
- Hash & user management CLI script.
- Proxy + TLS for production environments.

---

## License

MIT (sample code). Use at your own risk; review and harden for your environment.
