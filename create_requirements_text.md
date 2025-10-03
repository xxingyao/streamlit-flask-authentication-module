# Linux: requirements.txt with Nexus + local wheel

A quick, shareable guide for installing from your **Nexus** private index while also using a **local wheel** (e.g., your offline PyJWT wheel). This assumes your pip already defaults to Nexus via `pip.conf`.

---

## 1) Get the absolute path to your local wheel folder
Requirements files do **not** expand `~`, so convert `~/build_pyjwt` to an absolute `file://` path.

```bash
WHEELDIR="$(cd ~/build_pyjwt && pwd)"
echo "$WHEELDIR"   # e.g. /home/jovyan/build_pyjwt
```

---

## 2) Option A — Search your local wheel folder in addition to Nexus (recommended)
`requirements.txt`:
```txt
--find-links file:///home/jovyan/build_pyjwt

PyJWT==2.9.0
# others still come from Nexus by default
pandas==2.2.2
my-internal-lib==0.6.3
```
Install:
```bash
python -m pip install -r requirements.txt
```

---

## 3) Option B — Force this exact local wheel (never pull PyJWT from Nexus)
`requirements.txt`:
```txt
PyJWT==2.9.0 @ file:///home/jovyan/build_pyjwt/PyJWT-2.9.0-py3-none-any.whl
pandas==2.2.2
my-internal-lib==0.6.3
```
Install:
```bash
python -m pip install -r requirements.txt
```

---

## 4) Option C — Fully offline for this run (ignore Nexus entirely)
`requirements.txt`:
```txt
--no-index
--find-links file:///home/jovyan/build_pyjwt
PyJWT==2.9.0
```
Install:
```bash
python -m pip install -r requirements.txt
```

---

## 5) Verify installation
```bash
python - <<'PY'
import jwt, pathlib
print(jwt.__version__)
print(pathlib.Path(jwt.__file__).resolve())
PY
```

---

## 6) Nice-to-haves
**Integrity lock (hash pin):**
```bash
pip hash /home/jovyan/build_pyjwt/PyJWT-2.9.0-py3-none-any.whl
```
Then in `requirements.txt`:
```txt
--require-hashes
PyJWT==2.9.0 --hash=sha256:<paste_hash_here>
```

**Sanity-check your pip defaults:**
```bash
pip config list -v | sed -n 's/^global\.(index-url\|extra-index-url\|no-index).*/\0/p'
pip debug --verbose | grep -E "index|find_links|no_index"
```

---

## 7) Tips (Linux)
- Use **absolute** `file://` paths; no `~` expansion inside requirements files.
- Keep using `python -m pip` to guarantee you install into the **current venv**.
- If your path has spaces, rename the folder or quote the `--find-links` flag on the command line.
- You can repeat `--find-links` lines if you have multiple local wheel folders.
- Do **not** add `--extra-index-url` to avoid enabling PyPI fallback if you want strict Nexus-only behavior.

