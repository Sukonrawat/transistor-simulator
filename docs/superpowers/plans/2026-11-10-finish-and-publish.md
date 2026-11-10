# Finish and Publish `transistor-simulator` — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish the already-working ENG29 2121 Lab 02 Flask app to a public GitHub repository and prove it runs on localhost.

**Architecture:** No application code changes. Install Git and the GitHub CLI, commit the design and plan documents, verify the app over real HTTP, then create the public repository and push.

**Tech Stack:** Git for Windows, GitHub CLI (`gh`), Python 3.12 in `.venv`, Flask 3.x, PowerShell.

**Spec:** `docs/superpowers/specs/2026-11-10-finish-and-publish-design.md`

## Global Constraints

- All Python commands use `.venv\Scripts\python.exe` (the system `python` is 3.12.7 without Flask; the dependencies live in the venv).
- Server binds `127.0.0.1:5000` only.
- Tests must be green before every commit.
- Run every command from the repository root (all paths below are relative).
- Commit messages: English, area prefix (`docs:`, `web:`, `tests:`), per `AGENTS.md`.
- Repository: public, named `transistor-simulator`.
- Do not modify `dc_bias.py`, `app.py`, `templates/`, `static/`, `tests/`, `AGENTS.md` or existing `docs/*.md`. `README.md` may only be corrected where it misstates the repository (e.g. the test counts).
- Do not commit `.venv/` or `__pycache__/`.

## Review Focus

1. **`winget` in a non-interactive shell** — an unaccepted source agreement makes the install abort with a prompt error instead of installing; every `winget` call must pass the acceptance flags and be checked for exit code 0.
2. **Stale PATH after install** — `git`/`gh` may be missing from the current shell even though installed; Task 1 Step 4 prepends the real install directories for the session.
3. **Wrong interpreter** — running `python` instead of `.venv\Scripts\python.exe` gives `ModuleNotFoundError: flask`; every Task 2/4/6 command uses the venv path.
4. **Port 5000 already in use** — the demo can silently hit another process; Task 4 confirms the response contains this app's form before trusting any result, and frees the port afterwards.
5. **Thai text through PowerShell** — console encoding can mangle Thai assertions; Task 4 checks status codes and ASCII values first and only then the Thai error text.

---

### Task 1: Install Git and GitHub CLI

**Files:** none (machine tooling).

**Interfaces:**
- Consumes: nothing.
- Produces: `git` and `gh` on `PATH` for later tasks.

- [x] **Step 1: Install Git for Windows**

Run:
```powershell
winget install --id Git.Git -e --source winget --accept-source-agreements --accept-package-agreements --disable-interactivity
$LASTEXITCODE
```
Expected: `0`, or "No available upgrade found" when Git is already installed — in that case continue to Step 3.

- [x] **Step 2: Install the GitHub CLI**

Run:
```powershell
winget install --id GitHub.cli -e --source winget --scope user --accept-source-agreements --accept-package-agreements --disable-interactivity
$LASTEXITCODE
```
Expected: `0` and a "Successfully installed" line. Use `--scope user` when the machine-wide MSI is cancelled with exit code `1602` (no elevation prompt answered).

- [x] **Step 3: Verify both**

Run:
```powershell
git --version; gh --version
```
Expected: `git version 2.x` and `gh version 2.x`. If either is missing, the shell inherited a stale PATH — continue to Step 4.

- [x] **Step 4: Recover PATH in the current shell**

A newly spawned process inherits the PATH of the process that spawned it, so "a fresh shell" can still be stale. Prepend the real install directories for this session:
```powershell
$env:PATH = "$env:LOCALAPPDATA\Programs\Git\cmd;$env:LOCALAPPDATA\Microsoft\WinGet\Packages\GitHub.cli_Microsoft.Winget.Source_8wekyb3d8bbwe\bin;$env:PATH"
git --version; gh --version
```
Expected: both versions print. If a directory differs, find it with `Get-ChildItem $env:LOCALAPPDATA -Filter gh.exe -Recurse -Depth 6`. winget writes both directories to the *user* PATH; only processes started after that write inherit them.

No commit: this task changes the machine, not the repository.

---

### Task 2: Baseline the repository

**Files:** none.

**Interfaces:**
- Consumes: `git` from Task 1.
- Produces: confirmation that the tree is clean and the suite is green before any new commit.

- [x] **Step 1: Confirm the working tree is clean**

Run:
```powershell
git status --short
```
Expected: no output, or only `?? docs/superpowers/` before Task 3 commits it.

- [x] **Step 2: Confirm the existing history**

Run:
```powershell
git log --oneline
```
Expected: 5 commits, newest `66fba92 docs: add README, AGENTS conventions, validation, reflection and test log`.

- [x] **Step 3: Run the full suite**

Run:
```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -v
```
Expected: `Ran 18 tests` … `OK`.

---

### Task 3: Commit the design and plan documents

**Files:**
- Create: `docs/superpowers/specs/2026-11-10-finish-and-publish-design.md` (already written)
- Create: `docs/superpowers/plans/2026-11-10-finish-and-publish.md` (this file)

**Interfaces:**
- Consumes: clean tree from Task 2.
- Produces: one `docs:` commit; `HEAD` moves from `66fba92` to a new hash.

- [x] **Step 1: Stage only the new documents**

Run:
```powershell
git add docs/superpowers
git status --short
```
Expected: exactly two `A` entries, both under `docs/superpowers/`.

- [x] **Step 2: Review what is staged**

Run:
```powershell
git diff --staged --stat
```
Expected: two files, additions only, no `.venv/` or `__pycache__/`.

- [x] **Step 3: Commit**

Run:
```powershell
git commit -m "docs: add finish-and-publish design and implementation plan"
```
Expected: `2 files changed`, commit succeeds.

- [x] **Step 4: Confirm the new HEAD**

Run:
```powershell
git log --oneline -1
```
Expected: the new `docs:` commit on top of `66fba92`.

---

### Task 4: Verify the app end-to-end on localhost

**Files:** none.

**Interfaces:**
- Consumes: `.venv` Flask install; `app.py` routes `GET /`, `POST /calculate`.
- Produces: evidence the app serves the real form and real computed values over HTTP.

- [x] **Step 1: Start the server in the background and record its listener**

Run:
```powershell
Start-Process -FilePath ".venv\Scripts\python.exe" -ArgumentList "-m","flask","--app","app","run","--port","5000" -WindowStyle Hidden
Start-Sleep -Seconds 3
Get-NetTCPConnection -LocalPort 5000 -State Listen | Select-Object -ExpandProperty OwningProcess
```
Expected: exactly one process id. `Start-Process -PassThru` can return a shim pid that is not the listener, so take the pid from the port instead.

- [x] **Step 2: Confirm this app is on the port (not a stray process)**

Run:
```powershell
$page = Invoke-WebRequest -Uri "http://127.0.0.1:5000/" -UseBasicParsing
$page.StatusCode
foreach ($f in "vcc","r1","r2","rc","re","beta","vbe") { "$f = $($page.Content -match ('name="' + $f + '"'))" }
$page.Content -match '/calculate'
```
Expected: `200`, all seven field checks `True`, and `True`.

- [x] **Step 3: Submit the reference circuit**

Run:
```powershell
$body = @{vcc="12";r1="100000";r2="22000";rc="2200";re="1000";beta="100";vbe="0.7"}
$ok = Invoke-WebRequest -Uri "http://127.0.0.1:5000/calculate" -Method Post -Body $body -UseBasicParsing
$ok.StatusCode
foreach ($v in "1.942","1.242","9.294","8.052","1.230","Forward-Active") { "$v = $($ok.Content.Contains($v))" }
```
Expected: `200`, and every value `True`.

- [x] **Step 4: Submit an invalid resistor**

PowerShell mangles the Thai response, so probe with Python and write the script to a file first:
```powershell
@'
import urllib.error, urllib.parse, urllib.request
body = urllib.parse.urlencode({"vcc":"12","r1":"100000","r2":"22000","rc":"-5","re":"1000","beta":"100","vbe":"0.7"}).encode()
req = urllib.request.Request("http://127.0.0.1:5000/calculate", data=body, method="POST")
try:
    resp = urllib.request.urlopen(req, timeout=10); status, html = resp.status, resp.read().decode("utf-8")
except urllib.error.HTTPError as exc:
    status, html = exc.code, exc.read().decode("utf-8")
print(status, "RC" in html, "\u0e21\u0e32\u0e01\u0e01\u0e27\u0e48\u0e32 0" in html, "8.052" not in html, 'name="vcc"' in html)
'@ | Set-Content -Encoding utf8 "$env:TEMP\probe.py"
.venv\Scripts\python.exe "$env:TEMP\probe.py"
```
Expected: `400 True True True True` — status, field named, Thai rule text, no stale result, form still rendered.

- [x] **Step 5: Stop the server**

Run:
```powershell
Get-NetTCPConnection -LocalPort 5000 -State Listen | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
Start-Sleep -Seconds 1
(Get-NetTCPConnection -LocalPort 5000 -State Listen -ErrorAction SilentlyContinue) -eq $null
```
Expected: `True` (nothing is listening on 5000 any more).

---

### Task 5: Authenticate, create the public repository, push

**Files:** none (adds `origin` to `.git/config`).

**Interfaces:**
- Consumes: `gh` from Task 1, commits from Tasks 2–3.
- Produces: `origin` → `https://github.com/<account>/transistor-simulator.git`, public, with `main` pushed.

- [x] **Step 1: Check authentication**

Run:
```powershell
gh auth status
```
Expected: `Logged in to github.com account <name>`.

- [x] **Step 2: If not authenticated, run the browser login from the tool**

`gh auth login --web` prints a one-time code and then polls until the code is
authorised. It can be driven from a tool call by redirecting stdin and capturing
its output:
```powershell
Set-Content -Path "$env:TEMP\gh-enter.txt" -Value "`r`n" -NoNewline
$p = Start-Process -FilePath (Get-Command gh).Source -ArgumentList "auth","login","--hostname","github.com","--git-protocol","https","--web" -RedirectStandardInput "$env:TEMP\gh-enter.txt" -RedirectStandardOutput "$env:TEMP\gh-auth.out" -RedirectStandardError "$env:TEMP\gh-auth.err" -PassThru -WindowStyle Hidden
Start-Sleep -Seconds 6
Get-Content "$env:TEMP\gh-auth.err"
```
Expected: stderr shows `One-time code (XXXX-XXXX)` and the URL
`https://github.com/login/device`. Give both to the user, wait for them to
authorise, then re-run Step 1. Alternative if the browser flow is blocked: the
user sets `$env:GH_TOKEN` to a token with `repo` scope for this shell.

- [x] **Step 3: Create the public repository and push**

Run:
```powershell
gh repo create transistor-simulator --public --source . --remote origin --push
```
Expected: a `https://github.com/<account>/transistor-simulator` URL and a successful push of `main`. gh writes git's progress to stderr, so PowerShell may report a non-zero exit code even on success — confirm with Step 4 rather than the exit code.

- [x] **Step 4: Verify the remote, the pushed history and the visibility**

Run:
```powershell
git remote -v
"remote=$(git rev-parse origin/main)"
"local =$(git rev-parse HEAD)"
gh repo view transistor-simulator --json name,visibility,url,defaultBranchRef
```
Expected: `origin` on both fetch and push; the two hashes are identical; JSON with `"visibility":"PUBLIC"`, the repository URL and `"defaultBranchRef":{"name":"main"}`.

---

### Task 6: Final acceptance check

**Files:** none.

**Interfaces:**
- Consumes: everything above.
- Produces: the hand-off evidence for the lab report.

- [x] **Step 1: Re-run the suite on the published tree**

Run:
```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -v
```
Expected: `Ran 18 tests` … `OK`.

- [x] **Step 2: Confirm the tree is clean and history is complete**

Run:
```powershell
git status --short
git log --oneline -6
```
Expected: no output from `status`; 6 commits, newest the `docs:` commit.

- [x] **Step 3: Confirm the README's evidence exists**

Run:
```powershell
(Get-ChildItem docs\screenshots -Filter *.png).Count
```
Expected: `5`.

- [x] **Step 4: Confirm the published repository**

Run:
```powershell
gh repo view transistor-simulator --json visibility,url,defaultBranchRef
```
Expected: `PUBLIC`, the URL, and `defaultBranchRef.name` = `main`.

- [x] **Step 5: Report the demo command to the user**

State the exact commands:
```powershell
.venv\Scripts\python.exe -m flask --app app run
# open http://127.0.0.1:5000/
```
