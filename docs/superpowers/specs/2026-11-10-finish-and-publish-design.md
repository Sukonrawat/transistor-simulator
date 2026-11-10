# Finish and Publish `transistor-simulator` — Design

**Date:** 2026-11-10
**Status:** Approved — approach A, public repository
**Course:** ENG29 2121 · Lab 02 · BJT Common-Emitter DC Bias

## 1 · Intent and why

The Lab 02 web app already exists and passes its tests. What is missing is the
delivery: the code lives in a local repository that has never been pushed, and
`git` is not on the PATH this session inherits. This work finishes the
assignment by publishing the existing, verified application to GitHub and
demonstrating it running on localhost today.

No application behaviour changes.

## 2 · Current state (verified before this design)

- `dc_bias.py`, `app.py`, `templates/index.html`, `static/style.css`,
  `tests/` (18 tests), `docs/` including 5 screenshots.
- `.venv\Scripts\python.exe -m unittest discover -s tests -v` → **18 tests OK**
  (10 engineering + 8 HTTP).
- 5 commits on `main`, HEAD `66fba92`, working tree clean.
- `git --version` fails in this shell: Git 2.56 is installed under
  `%LOCALAPPDATA%\Programs\Git` but is absent from the inherited PATH.
  `.git/config` has no remote.

## 3 · Goals

1. Git and the GitHub CLI usable from this session.
2. Public GitHub repository `transistor-simulator` containing the 5 existing
   commits plus one commit for this design and its implementation plan.
3. The app verified end-to-end over HTTP on `127.0.0.1:5000`.

## 4 · Non-goals

- Any change to equations, validation rules, region thresholds, UI copy,
  templates or CSS.
- AC, transient, SPICE, FET, circuit editor, JSON API.
- CI, Docker, hosting, custom domain.

## 5 · Anti-goals (a failure even if it "works")

- Publishing a repository whose README references tests or screenshots that
  are absent.
- Committing `.venv/`, `__pycache__/` or other build artefacts.
- Changing the repository name or visibility without being asked.

## 6 · Constraints

- Python 3.10+; every command runs through `.venv\Scripts\python.exe`, because
  the system `python` (3.12.7) does not have Flask installed while the
  dependencies live in the 3.12 venv.
- The server binds `127.0.0.1:5000` only — never a public interface.
- A green test run precedes every commit (`AGENTS.md`).
- Commit messages are English, prefixed by area (`docs:`, `web:`, …).

## 7 · Approaches considered

| # | Approach | Trade-off | Verdict |
|---|---|---|---|
| **A** | Install Git + GitHub CLI; one interactive login; `gh repo create --public --source . --push` | Two installs and one human login, but auth, remote creation and push are one step | **Chosen** |
| B | Install Git only; the user creates an empty repo by hand and supplies the URL; push via Git Credential Manager | One fewer install, but a manual repo-creation step and a separate credential prompt | Rejected — no benefit over A |

Both reach the same end state; A removes the only manual step.

## 8 · Decisions

- **Repository name:** `transistor-simulator`, matching the directory, the
  README and the existing commits. The request wrote "transitor-simulator";
  treated as a typo.
- **Visibility:** public, as requested.
- **New documents:** `docs/superpowers/specs/` and `docs/superpowers/plans/`,
  written in English. User-facing material (UI, README, `AGENTS.md`, other
  `docs/`) stays Thai and is not touched.
- **Authentication:** `gh auth login --web` run from the agent's shell, with
  the one-time code handed to the user to authorise in their browser.

## 9 · Definition of done

- `git --version` and `gh --version` succeed.
- `.venv\Scripts\python.exe -m unittest discover -s tests -v` → 18 tests OK.
- `GET http://127.0.0.1:5000/` → 200 with the seven input fields.
- Reference submission → 200 showing VB 1.942 V, VE 1.242 V, VC 9.294 V,
  VCE 8.052 V, IC 1.230 mA, badge Forward-Active.
- `RC = -5` → 400 with a Thai message naming RC, form still rendered.
- `git status` clean; `origin` points at GitHub; `origin/main` equals `HEAD`;
  repository is public.

## 10 · Left to the builder

Exact install flags, PATH recovery, authentication hand-off and the HTTP
verification commands are specified in
`docs/superpowers/plans/2026-11-10-finish-and-publish.md`.
