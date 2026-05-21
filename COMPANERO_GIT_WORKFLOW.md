# Git & GitHub Workflow Guide
## Compañero AI — `gitMiguel27/Companero_AI`

> **How to use this guide:** Section 1 gets your Codespace connected to your repo right now — run those commands first. Section 2 is the daily loop you'll repeat every session. Section 3 maps out every feature branch for this specific project. Bookmark this — you'll come back to it constantly.

---

## Table of Contents

1. [Your Repo Right Now](#1-your-repo-right-now)
2. [One-Time Setup in Codespaces](#2-one-time-setup-in-codespaces)
3. [Your Branch Strategy](#3-your-branch-strategy)
4. [The Daily Git Loop](#4-the-daily-git-loop)
5. [Feature Branch Workflow — Step by Step](#5-feature-branch-workflow--step-by-step)
6. [Compañero AI Branch Roadmap](#6-compañero-ai-branch-roadmap)
7. [Pull Requests: Merging Features into Main](#7-pull-requests-merging-features-into-main)
8. [Undoing Mistakes](#8-undoing-mistakes)
9. [Quick Reference Cheat Sheet](#9-quick-reference-cheat-sheet)

---

## 1. Your Repo Right Now

Confirmed state of `https://github.com/gitMiguel27/Companero_AI`:

| Item | Status |
|---|---|
| Default branch | `main` |
| Total commits | 1 (initial README) |
| Files | `README.md` only |
| Feature branches | None yet |
| Remote URL | `https://github.com/gitMiguel27/Companero_AI.git` |

---

## 2. One-Time Setup in Codespaces

Run these **once**, in order, the first time you open your Codespace for this project. You won't need to repeat them unless you create a brand-new Codespace.

### Step 2.1 — Confirm your remote is connected

```bash
git remote -v
```

Expected output:

```
origin  https://github.com/gitMiguel27/Companero_AI.git (fetch)
origin  https://github.com/gitMiguel27/Companero_AI.git (push)
```

If you see nothing, add the remote manually:

```bash
git remote add origin https://github.com/gitMiguel27/Companero_AI.git
```

---

### Step 2.2 — Pull your README down locally

Your GitHub already has a commit. Pull it so your local Codespace matches:

```bash
git pull origin main
```

You should see `README.md` appear in your file tree.

---

### Step 2.3 — Set your Git identity

```bash
git config --global user.name "Miguel"
git config --global user.email "your-github-email@example.com"
```

Use the same email as your GitHub account so your commits are attributed correctly on the profile graph.

---

### Step 2.4 — Confirm your starting position

```bash
git branch
```

Output should show `* main`. The `*` means "this is where I am."

```bash
git log --oneline
```

Should show 1 commit — your initial README.

---

### Step 2.5 — Scaffold the project, then make your first real commit

After creating all your folders and `__init__.py` files from the implementation plan (Phase 1), commit everything to main as your foundation:

```bash
# Stage everything
git add .

# Verify what you're about to commit
git status

# Commit
git commit -m "chore: initialize project structure with uv, folders, and env config"

# Push to GitHub
git push origin main
```

> **Check:** Refresh `https://github.com/gitMiguel27/Companero_AI` — your `core/`, `memory/`, `state/`, `ui/`, and `uploads/` folders should now appear.

---

## 3. Your Branch Strategy

`main` is always clean and working. Every feature lives in its own branch until it's tested and ready to merge.

```
main ────────────────────────────────────────────────────────── (always stable)
         │               │                │               │
         └─ feat/        └─ feat/         └─ feat/        └─ feat/
            scaffold        ingestor         llm-core        chromadb
            (done→PR)       (done→PR)        (in progress)   (next)
```

### Branch Naming Convention

Always follow this format: `feat/short-description` or `fix/short-description`

| Branch Name | Purpose |
|---|---|
| `main` | Stable, working code only. **Never code directly here.** |
| `feat/project-scaffold` | Folder structure, `pyproject.toml`, `.env`, `.gitignore` |
| `feat/ingestor` | `core/ingestor.py` — PDF + text chunking with pdfplumber |
| `feat/llm-core` | `core/llm.py`, `core/prompts.py` — Ollama + Spanish prompts |
| `feat/chromadb` | `memory/` layer — embeddings, vector store, retrieval |
| `feat/study-sheet` | `core/study_sheet.py` — generation chains (text, PDF, RAG) |
| `feat/questions` | `core/questions.py` — question generation + parser |
| `feat/streamlit-ui` | `app.py`, all `ui/` modules — full Streamlit interface |
| `feat/rewards` | `state/session.py`, `ui/rewards_view.py` — badges system |
| `feat/voice-io` | Future: `core/tts.py`, `core/stt.py` — TTS/STT on local Mac |
| `fix/bug-description` | Any bug fix on an existing feature |

> **Rule:** One feature = one branch. Small, focused branches are easier to review, easier to merge, and easier to roll back if something breaks.

---

## 4. The Daily Git Loop

Every coding session follows this rhythm. Internalize it — it protects you from losing work and keeps your history readable.

```
1.  Start on main             →  git checkout main
2.  Pull latest               →  git pull origin main
3.  Switch to feature branch  →  git checkout feat/your-feature
4.  Write code
5.  Check what changed        →  git status
6.  Stage changes             →  git add .
7.  Commit with message       →  git commit -m "feat: ..."
8.  Push to GitHub            →  git push
9.  (When feature is done)       Open PR on GitHub → merge → delete branch
10. Back to step 1
```

---

## 5. Feature Branch Workflow — Step by Step

### Starting a new feature

Always branch off a fresh `main`:

```bash
# 1. Make sure you're on main
git checkout main

# 2. Pull any changes (critical if you've been working across sessions)
git pull origin main

# 3. Create and switch to your new feature branch in one command
git checkout -b feat/ingestor
```

> `git checkout -b` creates the branch AND switches to it simultaneously. Confirm with `git branch` — you should see `* feat/ingestor`.

---

### While building the feature

Commit small and often. Think of each commit as a save point.

```bash
# See what files have changed since your last commit
git status

# See the actual line-by-line changes
git diff

# Stage one specific file (better practice than always staging everything)
git add core/ingestor.py

# Stage all changes at once
git add .

# Commit with a clear, prefixed message
git commit -m "feat: add pdfplumber extraction and text chunker with overlap"
```

### Commit message prefixes

| Prefix | When to use |
|---|---|
| `feat:` | Adding a new file or feature |
| `fix:` | Fixing a bug |
| `refactor:` | Restructuring without changing behavior |
| `docs:` | README, comments, docstrings |
| `style:` | Formatting, whitespace, naming |
| `test:` | Test scripts |
| `chore:` | Config, dependencies, `.gitignore` |

**Real examples for this project:**

```bash
git commit -m "feat: add Ollama LLM module with temperature config"
git commit -m "feat: add Spanish study sheet and question prompt templates"
git commit -m "feat: add ChromaDB store_chunks and retrieve_context functions"
git commit -m "fix: handle None return from pdfplumber on image-only pages"
git commit -m "docs: add docstrings to all ingestor functions"
git commit -m "refactor: move chunk_text logic to its own helper function"
```

---

### Push your feature branch to GitHub

```bash
# First push — sets the upstream tracking link
git push -u origin feat/ingestor

# All future pushes on the same branch (shorter)
git push
```

After the first `-u` push, Git remembers where this branch lives on GitHub. From then on, just `git push`.

---

### Check your status at any time

```bash
git branch                       # Which branch am I on?
git status                       # What's changed since my last commit?
git log --oneline                # My commit history (newest first)
git log --oneline --graph --all  # Visual map of all branches
```

---

## 6. Compañero AI Branch Roadmap

Here's the exact sequence to build and merge each feature, matched to the implementation plan phases.

---

### Phase 0 — Scaffold (commit directly to `main`, just once)

```bash
# You're already on main after setup
# Create folder structure and config files, then:
git add .
git commit -m "chore: initialize project structure, uv setup, env config"
git push origin main
```

---

### Phase 1 — PDF Ingestor → `feat/ingestor`

```bash
git checkout main && git pull origin main
git checkout -b feat/ingestor

# Build: core/ingestor.py
git add core/ingestor.py
git commit -m "feat: add pdfplumber PDF extraction"

# After testing with test_ingestor.py:
git add core/ingestor.py
git commit -m "feat: add chunk_text with overlap and ingest_raw_text helper"

git push -u origin feat/ingestor
# → Open PR on GitHub → Merge → Delete branch
```

---

### Phase 2 — LLM Core → `feat/llm-core`

```bash
git checkout main && git pull origin main
git checkout -b feat/llm-core

# Build: core/llm.py
git add core/llm.py
git commit -m "feat: add Ollama LLM module with temperature config"

# Build: core/prompts.py
git add core/prompts.py
git commit -m "feat: add Spanish prompt templates for study sheet, questions, topic extraction, and RAG"

git push -u origin feat/llm-core
# → Open PR → Merge → Delete branch
```

---

### Phase 3 — ChromaDB Memory → `feat/chromadb`

```bash
git checkout main && git pull origin main
git checkout -b feat/chromadb

# Build: memory/embeddings.py
git add memory/embeddings.py
git commit -m "feat: add sentence-transformer embeddings config"

# Build: memory/vector_store.py
git add memory/vector_store.py
git commit -m "feat: add ChromaDB store_chunks, retrieve_context, and get_stored_topics"

git push -u origin feat/chromadb
# → Open PR → Merge → Delete branch
```

---

### Phase 4 — Study Sheet Chain → `feat/study-sheet`

```bash
git checkout main && git pull origin main
git checkout -b feat/study-sheet

# Build: core/study_sheet.py
git add core/study_sheet.py
git commit -m "feat: add generate_study_sheet with text, PDF, and RAG memory modes"

git push -u origin feat/study-sheet
# → Open PR → Merge → Delete branch
```

---

### Phase 5 — Questions Chain → `feat/questions`

```bash
git checkout main && git pull origin main
git checkout -b feat/questions

# Build: core/questions.py
git add core/questions.py
git commit -m "feat: add Spanish question generator with P/R format parser"

git push -u origin feat/questions
# → Open PR → Merge → Delete branch
```

---

### Phase 6 — Full Streamlit UI → `feat/streamlit-ui`

This is the largest branch — commit module by module rather than all at once.

```bash
git checkout main && git pull origin main
git checkout -b feat/streamlit-ui

# Session state
git add state/session.py
git commit -m "feat: add session state init and milestone check_and_award_badges"

# App entry point
git add app.py
git commit -m "feat: add Streamlit app entry point with tab layout"

# Sidebar
git add ui/sidebar.py
git commit -m "feat: add sidebar with text, PDF, and memory input modes"

# Study view
git add ui/study_view.py
git commit -m "feat: add study sheet display tab with download button"

# Quiz view
git add ui/quiz_view.py
git commit -m "feat: add practice quiz tab with reveal mechanic and progress bar"

# Rewards view
git add ui/rewards_view.py
git commit -m "feat: add rewards tab with badge catalog and locked badge tips"

git push -u origin feat/streamlit-ui
# → Open PR → Merge → Delete branch
```

---

### Future Phase — Voice I/O → `feat/voice-io`

```bash
git checkout main && git pull origin main
git checkout -b feat/voice-io

# Build when ready:
# core/tts.py  — pyttsx3 Spanish TTS
# core/stt.py  — Whisper transcription
# ui/voice_controls.py — Streamlit audio input

git push -u origin feat/voice-io
# Do NOT merge until fully tested locally on your Intel Mac
# (voice I/O requires mic access — test outside Codespaces)
```

---

## 7. Pull Requests: Merging Features into Main

A Pull Request (PR) is the formal step of bringing a feature branch into `main`. Even as a solo developer, PRs give you a clean, reviewable history — and your instructor will see this on GitHub.

### Opening a PR

1. Push your branch: `git push -u origin feat/your-branch`
2. Go to `https://github.com/gitMiguel27/Companero_AI`
3. GitHub shows a yellow banner: **"feat/your-branch had recent pushes"** → click **Compare & pull request**
4. Fill in the PR description like this:

```
Title:
feat: add ChromaDB memory layer

Body:
## What this adds
- memory/embeddings.py — sentence-transformer embedding config
- memory/vector_store.py — store_chunks, retrieve_context, get_stored_topics
- ChromaDB persisted to ./chroma_db (excluded from git)

## How to test
Run test_chroma.py:
  python test_chroma.py
Expected: chunks stored, context retrieved, topic "mitosis" in topics list

## Notes
- chroma_db/ folder is gitignored — each Codespace builds its own local DB
```

5. Click **Create pull request**
6. Click **Merge pull request** → **Confirm merge**
7. Click **Delete branch** (keeps your repo tidy)

---

### After every merge — clean up locally

```bash
# Return to main and pull the merged commit down
git checkout main
git pull origin main

# Delete the local copy of the feature branch (already merged, no longer needed)
git branch -d feat/your-branch
```

---

### Viewing your branch history after several merges

```bash
git log --oneline --graph --all
```

You'll see something like this — a clean, readable project timeline:

```
* a3f92c1 (HEAD -> main) Merge pull request #5 — feat/streamlit-ui
* 7d14e88 Merge pull request #4 — feat/questions
* 4c2b91a Merge pull request #3 — feat/study-sheet
* 1e7f330 Merge pull request #2 — feat/chromadb
* 9a84c12 Merge pull request #1 — feat/llm-core
* 3b10d07 chore: initialize project structure
* f2a891e Initial commit (README)
```

---

## 8. Undoing Mistakes

### "I haven't committed yet — I want to discard my changes"

```bash
# Undo changes to one specific file
git checkout -- core/llm.py

# Undo ALL uncommitted changes (permanent — be careful)
git restore .
```

---

### "I committed but haven't pushed — I want to undo the commit"

```bash
# Undo the commit but KEEP the file changes (so you can fix and recommit)
git reset --soft HEAD~1
```

---

### "I want to fix my last commit message"

```bash
# Only works before pushing
git commit --amend -m "feat: corrected and clearer commit message"
```

---

### "I pushed a bad commit and need to undo it safely"

```bash
# Creates a NEW commit that reverses the bad one — safe for pushed branches
git revert HEAD
git push
```

> Never use `git reset --hard` on commits you've already pushed. It rewrites history and can cause problems.

---

### "I accidentally started coding on main instead of a feature branch"

```bash
# 1. Stash your changes (saves them temporarily without committing)
git stash

# 2. Create and switch to the correct feature branch
git checkout -b feat/the-right-branch

# 3. Restore your stashed work onto the new branch
git stash pop

# 4. Now commit normally
git add .
git commit -m "feat: ..."
```

---

### "I want to see what's different between my branch and main"

```bash
git diff main..feat/your-branch
```

---

### "ChromaDB or upload files are showing up in git status — how do I stop that?"

```bash
# Confirm your .gitignore includes:
cat .gitignore
# Should contain: chroma_db/ and uploads/*.pdf

# If files were already tracked before you added them to .gitignore:
git rm -r --cached chroma_db/
git rm --cached uploads/yourfile.pdf
git commit -m "chore: remove chroma_db and uploads from tracking"
```

> This is a Compañero AI-specific gotcha — `chroma_db/` gets created automatically the first time you run ChromaDB. Make sure it's in `.gitignore` before your first `git add .`.

---

## 9. Quick Reference Cheat Sheet

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SETUP & ORIENTATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
git remote -v                     # confirm GitHub connection
git pull origin main              # get latest from GitHub
git branch                        # which branch am I on? (* = current)
git log --oneline                 # short commit history
git log --oneline --graph --all   # visual branch map

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  BRANCHING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
git checkout -b feat/name         # create + switch to new branch
git checkout main                 # switch back to main
git branch -d feat/name           # delete local branch (after merge)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SAVING WORK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
git status                        # what's changed?
git diff                          # line-by-line changes
git add core/ingestor.py          # stage one file
git add .                         # stage all changes
git commit -m "feat: ..."         # save with message
git push -u origin feat/name      # first push of a branch
git push                          # push (after first time)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  UNDOING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
git restore .                     # undo all uncommitted changes
git reset --soft HEAD~1           # undo last commit, keep files
git commit --amend -m "..."       # fix last commit message (pre-push only)
git stash                         # temporarily save uncommitted work
git stash pop                     # restore stashed work
git revert HEAD                   # safely undo a pushed commit

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  COMPAÑERO AI — BRANCH ORDER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. main              ← scaffold (folders, pyproject.toml, .env)
2. feat/ingestor     ← pdfplumber + chunker
3. feat/llm-core     ← Ollama + Spanish prompts
4. feat/chromadb     ← embeddings + vector store
5. feat/study-sheet  ← study sheet chains (text, PDF, RAG)
6. feat/questions    ← question generator + parser
7. feat/streamlit-ui ← app.py + all ui/ modules
8. feat/rewards      ← session state + badge system
9. feat/voice-io     ← (future) TTS/STT — test locally, not Codespaces

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  THE FEATURE BRANCH LOOP (run every session)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
git checkout main
git pull origin main
git checkout -b feat/my-feature
  ... write code ...
git add .
git commit -m "feat: what I built"
git push -u origin feat/my-feature
  → GitHub: open PR → Merge → Delete branch
git checkout main
git pull origin main
git branch -d feat/my-feature
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

*Compañero AI — `gitMiguel27/Companero_AI` | CAP 942 Capstone*
