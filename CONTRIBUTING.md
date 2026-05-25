# Contributing to DevOps Learning Lab

Thank you for helping improve this project! Contributions of all kinds are welcome — new lessons, bug fixes, documentation improvements, and tooling enhancements.

## Ways to contribute

- **Add a new lesson** — fill a gap in the curriculum
- **Improve an existing lesson** — fix typos, add better examples, extend exercises
- **Fix a bug** — in the backend, frontend, or infrastructure
- **Improve documentation** — README, lesson content, inline comments
- **Report an issue** — use the [issue tracker](../../issues)

---

## Development setup

**Requirements:** Docker with Compose v2, ~4 GB RAM free, macOS/Linux/WSL2.

```bash
git clone https://github.com/estebanmorenoit/devops-learning-lab.git
cd devops-learning-lab
./start.sh build
```

The app is now available at **http://localhost:3000**.

**Useful dev commands:**

```bash
./start.sh logs          # tail backend + frontend logs
./start.sh restart       # restart backend after Python changes (no rebuild)
./start.sh shell         # open a bash shell in the backend container
```

Frontend changes to `frontend/index.html` are served by nginx immediately — no rebuild needed.

---

## Running the tests

Tests live in `backend/tests/` and run against the real lesson content.

**Inside the running container (recommended):**

```bash
./start.sh shell
python -m pytest tests/ -v
```

**Or directly if you have Python 3.12+ and the dependencies:**

```bash
pip install -r backend/requirements.txt pytest httpx
cd backend
DATA_DIR=/tmp/devops-lab python -m pytest tests/ -v
```

All 296 tests must pass before a PR is merged.

---

## Adding a lesson

1. Create a JSON file in `backend/lessons/content/<category>/<key>.json`
2. Register it in `backend/lessons/registry.py` by adding a tuple to `LESSON_ORDER`
3. Run the tests to verify the schema is valid
4. Open a PR with a short description of what the lesson covers

### Lesson JSON schema

```json
{
  "title": "Lesson Title",
  "phase": "category-slug",
  "week": 1,
  "category": "Display Category",
  "duration": "~45 min",
  "summary": "One-paragraph summary shown on the dashboard.",
  "sections": [
    {
      "id": "section-slug",
      "title": "Section Title",
      "type": "lesson",
      "body": "Markdown content here..."
    },
    {
      "id": "quiz",
      "title": "Quiz",
      "type": "quiz",
      "questions": [
        {
          "q": "Question text?",
          "options": ["Option A", "Option B", "Option C", "Option D"],
          "answer": 0,
          "explanation": "Why the answer is correct."
        }
      ]
    },
    {
      "id": "challenge",
      "title": "Challenge",
      "type": "challenge",
      "goal": "What the learner should accomplish.",
      "hints": ["Hint 1", "Hint 2"],
      "success_criteria": ["Criterion 1", "Criterion 2"]
    }
  ]
}
```

**Section types:**
- `lesson` / `exercise` — require a `body` field (Markdown)
- `quiz` — require a `questions[]` array; `answer` is a **zero-based integer index** into `options[]`
- `challenge` — require `goal`, `hints[]`, and `success_criteria[]`

**Code fences in body:**
- ` ```bash ` — interactive, shows a "▶ run" button in the UI
- ` ```bash norun ` — display-only code (no run button)
- ` ```yaml `, ` ```json `, etc. — always display-only

---

## Registry tuple format

```python
(phase, week, key, title, category, subdir, difficulty)
```

| Field | Description |
|---|---|
| `phase` | Groups lessons in the sidebar (e.g. `"kubernetes"`) |
| `week` | Ordering within the phase (integer) |
| `key` | Unique ID — must match the JSON filename (without `.json`) |
| `title` | Display name shown in the UI |
| `category` | Label shown on the lesson card |
| `subdir` | Subdirectory under `content/` |
| `difficulty` | `"beginner"`, `"intermediate"`, or `"advanced"` |

---

## Pull request checklist

- [ ] Tests pass: `python -m pytest tests/ -v` (296 tests)
- [ ] New lesson JSON validates against the schema (caught by tests)
- [ ] Frontend changes tested in browser at http://localhost:3000
- [ ] PR description explains the "why" — what gap this fills or what was broken

---

## Code style

- **Python** — standard library style, no external formatter required
- **JSON** — 2-space indentation (match existing files)
- **Shell** — `set -euo pipefail` at the top of every script
- **Frontend** — vanilla JS, no build step, keep it in `frontend/index.html`

---

## Need help?

Open an issue and use the **Question** label. Response time is best-effort.
