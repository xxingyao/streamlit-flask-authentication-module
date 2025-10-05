# Flask + Streamlit Authentication System

## Overview
This project demonstrates a simple authentication gateway using Flask as an authentication provider and Streamlit as a protected frontend app. Users must log in via the Flask app to access the Streamlit app.

---

## `flask_auth` (Flask Authentication Gateway)
- Provides user registration and login endpoints.
- Stores users in memory (demo only; not persistent).
- Issues stateless session IDs (sid) using HMAC-SHA256.
- Maintains an in-memory session store to prevent sid reuse.
- `/register`: Register a new user account.
- `/login`: Log in with username and password. On success, redirects to the Streamlit app with a session ID in the URL.
- `/verify`: Streamlit app uses this endpoint to verify session IDs.
- `/logout`: Invalidates the session ID.
- `/healthz`: Health check endpoint.

---

## `streamlit_app` (Protected Streamlit Frontend)
- Requires authentication for all content.
- Reads the session ID (sid) from the URL query parameter.
- Verifies the session ID with the Flask backend before rendering any content.
- If not authenticated, redirects the user to the Flask login page.
- After successful login, displays protected content (or a special admin page if the user is admin).
- Allows users to log out, which invalidates the session on the Flask backend.

---

## Usage
1. Start the Flask app (`flask_auth/app.py`).
2. Start the Streamlit app (`streamlit_app/app_streamlit.py`).
3. Register a new user at `/register` (e.g., http://localhost:5000/register).
4. Log in at `/login` (e.g., http://localhost:5000/login).
5. On successful login, you will be redirected to the Streamlit app with a session ID.
6. The Streamlit app will only render content if the session is valid.
7. Reloading the webpage while the session is active can still render the content.
8. Logging out will invalidate the session.

---

## Notes
- This demo uses in-memory storage for users and sessions. All data will be lost if the server restarts.
- For production, use a persistent database and secure session management.
- Session IDs are single-use and cannot be reused after logout.
