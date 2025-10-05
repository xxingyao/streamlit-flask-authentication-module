import os
import streamlit as st
import urllib.request, urllib.error, json

# ----- Config -----
FLASK_BASE = os.environ.get("FLASK_BASE", "http://localhost:5000")
FLASK_VERIFY = f"{FLASK_BASE}/verify"
FLASK_LOGOUT = f"{FLASK_BASE}/logout"
FLASK_LOGIN  = f"{FLASK_BASE}/login"

st.set_page_config(page_title="My Protected App", page_icon="🔐")

# ----- Back-compat helpers for query params -----
def _get_sid_from_url():
    # Try new API (1.30+)
    try:
        qp = st.query_params
        sid = qp.get("sid")
        if isinstance(sid, list):
            sid = sid[0]
        if sid:
            return sid
    except Exception:
        pass
    # Fallback for older Streamlit
    try:
        qp = st.experimental_get_query_params()
        sid_list = qp.get("sid")
        return sid_list[0] if sid_list else None
    except Exception:
        return None

def _clear_sid_from_url():
    try:
        st.query_params.clear()
        return
    except Exception:
        pass
    try:
        st.experimental_set_query_params()
    except Exception:
        pass

# ----- Small HTTP helper -----
def _post_text(url: str, data: str, timeout: float = 10.0):  # allow longer for cold start
    req = urllib.request.Request(
        url, data=data.encode("utf-8"), method="POST",
        headers={"Content-Type": "text/plain"}
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.getcode(), json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, {}
    except Exception:
        return 0, {}

# ----- Auth gate -----
def require_auth():
    if st.session_state.get("user") and st.session_state.get("sid"):
        return

    sid = _get_sid_from_url()

    if not sid:
        st.markdown(
            f'<meta http-equiv="refresh" content="0; url={FLASK_LOGIN}">',
            unsafe_allow_html=True
        )
        st.stop()

    code, payload = _post_text(FLASK_VERIFY, sid)
    if code != 200 or not payload.get("ok"):
        st.error(f"Session invalid or expired. Please log in again. (status={code}, payload={payload})")
        st.stop()

    st.session_state.sid = sid
    st.session_state.user = payload["user"]
    st.session_state.roles = payload.get("roles", [])
    # Do NOT clear sid from URL, so user stays logged in after refresh

def logout_and_redirect():
    sid = st.session_state.get("sid")
    if sid:
        _post_text(FLASK_LOGOUT, sid)
    st.session_state.clear()
    st.markdown(
        f'<meta http-equiv="refresh" content="0; url={FLASK_LOGIN}">', 
        unsafe_allow_html=True
    )
    st.stop()

# ---- Gate the app ----
require_auth()

# ---- Protected UI ----
st.sidebar.write(f"Signed in as **{st.session_state.user}**")
if st.sidebar.button("Log out"):
    logout_and_redirect()

if st.session_state.user == "admin":
    st.title("This is Admin Page.")
else:
    st.title("✅ Protected content")
    st.write("This only renders after successful verification with the Flask gateway.")
