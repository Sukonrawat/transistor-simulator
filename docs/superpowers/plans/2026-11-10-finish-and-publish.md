# Finish and Publish `transistor-simulator` — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish the already-working ENG29 2121 Lab 02 Flask app to a public GitHub repository and prove it runs on localhost.

**Architecture:** No application code changes. Install Git and the GitHub CLI, commit the design and plan documents, verify the app over real HTTP, then create the public repository and push.

**Tech Stack:** Git for Windows, GitHub CLI (`gh`), Python 3.12 in `.venv`, Flask 3.x, PowerShell.

**Spec:** `docs/superpowers/specs/2026-11-10-finish-and-publish-design.md`

## Global Constraints

- All Python commands use `.venv\Scripts\python.exe` (system `python` is 3.14; Flask lives in the 3.12 venv).
- Server binds `127.0.0.1:5000` only.
- Tests must be green before every commit.
- Commit messages: English, area prefix (`docs:`, `web:`, `tests:`), per `AGENTS.md`.
- Repository: public, named `transistor-simulator`.
- Do not modify `dc_bias.py`, `app.py`, `templates/`, `static/`, `tests/`, `README.md`, `AGENTS.md` or existing `docs/*.md`.
- Do not commit `.venv/` or `__pycache__/`.

## Review Focus

1. **`winget` in a non-interactive shell** — an unaccepted source agreement makes the install abort with a prompt error instead of installing; every `winget` call must pass the acceptance flags and be checked for exit code 0.
2. **Stale PATH after install** — `git`/`gh` may be missing from the current shell even though installed; Task 1 verifies in a fresh shell and falls back to an explicit PATH entry.
3. **Wrong interpreter** — running `python` instead of `.venv\Scripts\python.exe` gives `ModuleNotFoundError: flask`; every Task 2/4/6 command uses the venv path.
4. **Port 5000 already in use** — the demo can silently hit another process; Task 4 confirms the response contains this app's form before trusting any result, and frees the port afterwards.
5. **Thai text through PowerShell** — console encoding can mangle Thai assertions; Task 4 checks status codes and ASCII values first and only then the Thai error text.

---

### Task 1: Install Git and GitHub CLI

**Files:** none (machine tooling).

**Interfaces:**
- Consumes: nothing.
- Produces: `git` and `gh` on `PATH` for later tasks.

- [ ] **Step 1: Install Git for Windows**

Run:
```powershell
winget install --id Git.Git -e --source winget --accept-source-agreements --accept-package-agreements --disable-interactivity
```
Expected: exit code 0 and a "Successfully installed" line.

- [ ] **Step 2: Install the GitHub CLI**

Run:
```powershell
winget install --id GitHub.cli -e --source winget --accept-source-agreements --accept-package-agreements --disable-interactivity
```
Expected: exit code 0 and a "Successfully installed" line.

- [ ] **Step 3: Verify both in a fresh shell**

Run:
```powershell
git --version; gh --version
```
Expected: `git version 2.x` and `gh version 2.x`.

- [ ] **Step 4: Recover PATH if either is missing**

Only if Step 3 failed, run:
```powershell
$env:PATH = "C:\Program Files\Git\cmd;C:\Program Files\GitHub CLI;$env:PATH"
git --version; gh --version
```
Expected: both versions print. If the install directory differs, locate it with `Get-ChildItem 'C:\Program Files' -Filter git.exe -Recurse -Depth 3` and prepend that directory instead.

No commit: this task changes the machine, not the repository.

---

### Task 2: Baseline the repository

**Files:** none.

**Interfaces:**
- Consumes: `git` from Task 1.
- Produces: confirmation that the tree is clean and the suite is green before any new commit.

- [ ] **Step 1: Confirm the working tree is clean**

Run:
```powershell
git status --short
```
Expected: no output.

- [ ] **Step 2: Confirm the existing history**

Run:
```powershell
git log --oneline
```
Expected: 5 commits, newest `66fba92 docs: add README, AGENTS conventions, validation, reflection and test log`.

- [ ] **Step 3: Run the full suite**

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

- [ ] **Step 1: Stage only the new documents**

Run:
```powershell
git add docs/superpowers
git status --short
```
Expected: exactly two `A` entries, both under `docs/superpowers/`.

- [ ] **Step 2: Review what is staged**

Run:
```powershell
git diff --staged --stat
```
Expected: two files, additions only, no `.venv/` or `__pycache__/`.

- [ ] **Step 3: Commit**

Run:
```powershell
git commit -m "docs: add finish-and-publish design and implementation plan"
```
Expected: `2 files changed`, commit succeeds.

- [ ] **Step 4: Confirm the new HEAD**

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

- [ ] **Step 1: Start the server in the background**

Run:
```powershell
$server = Start-Process -FilePath ".venv\Scripts\python.exe" -ArgumentList "-m","flask","--app","app","run","--port","5000" -PassThru -WindowStyle Hidden
Start-Sleep -Seconds 3
$server.Id
```
Expected: a process id is printed and the port answers within 3 s.

- [ ] **Step 2: Confirm this app is on the port (not a stray process)**

Run:
```powershell
$page = Invoke-WebRequest -Uri "http://127.0.0.1:5000/" -UseBasicParsing
$page.StatusCode
$page.Content -match 'name="vcc"' -and $page.Content -match '/calculate'
```
Expected: `200` and `True`.

- [ ] **Step 3: Submit the reference circuit**

Run:
```powershell
$body = @{vcc="12";r1="100000";r2="22000";rc="2200";re="1000";beta="100";vbe="0.7"}
$ok = Invoke-WebRequest -Uri "http://127.0.0.1:5000/calculate" -Method Post -Body $body -UseBasicParsing
$ok.StatusCode
foreach ($v in "1.942","1.242","9.294","8.052","1.230","Forward-Active") { "$v = $($ok.Content.Contains($v))" }
```
Expected: `200`, and every value `True`.

- [ ] **Step 4: Submit an invalid resistor**

Run:
```powershell
$bad = @{vcc="12";r1="100000";r2="22000";rc="-5";re="1000";beta="100";vbe="0.7"}
try { Invoke-WebRequest -Uri "http://127.0.0.1:5000/calculate" -Method Post -Body $bad -UseBasicParsing } catch { $r = $_.Exception.Response }
[int]$r.StatusCode
```
Expected: `400` (the page still renders; it is a validation response, not a crash).

- [ ] **Step 5: Stop the server**

Run:
```powershell
Stop-Process -Id $server.Id -Force
```
Expected: no error; `http://127.0.0.1:5000/` no longer answers.

---

### Task 5: Authenticate, create the public repository, push

**Files:** none (adds `origin` to `.git/config`).

**Interfaces:**
- Consumes: `gh` from Task 1, commits from Tasks 2–3.
- Produces: `origin` → `https://github.com/<account>/transistor-simulator.git`, public, with `main` pushed.

- [ ] **Step 1: Check authentication**

Run:
```powershell
gh auth status
```
Expected: `Logged in to github.com account <name>`.

- [ ] **Step 2: If not authenticated, hand off to the user**

Ask the user to run this in their own terminal (it opens a browser and cannot be completed from a tool call):
```powershell
gh auth login --hostname github.com --git-protocol https --web
```
Then re-run Step 1. Alternative if the browser flow is blocked: the user sets `$env:GH_TOKEN` to a token with `repo` scope for this shell.

- [ ] **Step 3: Create the public repository and push**

Run:
```powershell
gh repo create transistor-simulator --public --source . --remote origin --push
```
Expected: a `https://github.com/<account>/transistor-simulator` URL and a successful push of `main`.

- [ ] **Step 4: Verify the remote and visibility**

Run:
```powershell
git remote -v
gh repo view transistor-simulator --json name,visibility,url,defaultBranchRef
```
Expected: `origin` on both fetch and push; JSON with `"visibility":"PUBLIC"` and the repository URL.

---

### Task 6: Final acceptance check

**Files:** none.

**Interfaces:**
- Consumes: everything above.
- Produces: the hand-off evidence for the lab report.

- [ ] **Step 1: Re-run the suite on the published tree**

Run:
```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -v
```
Expected: `Ran 18 tests` … `OK`.

- [ ] **Step 2: Confirm the tree is clean and history is complete**

Run:
```powershell
git status --short
git log --oneline -6
```
Expected: no output from `status`; 6 commits, newest the `docs:` commit.

- [ ] **Step 3: Confirm the README's evidence exists**

Run:
```powershell
(Get-ChildItem docs\screenshots -Filter *.png).Count
```
Expected: `5`.

- [ ] **Step 4: Confirm the published repository**

Run:
```powershell
gh repo view transistor-simulator --json visibility,url,defaultBranchRef
```
Expected: `PUBLIC`, the URL, and `defaultBranchRef.name` = `main`.

- [ ] **Step 5: Report the demo command to the user**

State the exact commands:
```powershell
.venv\Scripts\Activate.ps1
python -m flask --app app run
# open http://127.0.0.1:5000/
```
