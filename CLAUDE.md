# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MAM is a personal/family financial records management web app with a Chinese-language UI. Built with Flask, SQLite, Bootstrap 5, and ECharts. Tracks expenses for two users (CHEN/DAN) across multiple accounts with visualization.

## Commands

### Install Dependencies
```bash
uv sync                    # canonical method
pip install -r requirements.txt   # legacy fallback
```

### Run the Application
```bash
uv run main.py             # runs on 0.0.0.0:5000, debug mode
python main.py             # same, without uv
FLASK_APP=main.py flask run
```

### Testing
```bash
uv run pytest              # run all tests (none exist yet)
uv run pytest tests/test_file.py::test_function_name   # single test
uv run pytest --cov=. --cov-report=html                # with coverage
```

### Linting
```bash
ruff check .               # no config file, runs on defaults
ruff format .
```

### Docker
```bash
docker compose up --build  # exposes port 5000
```

## Architecture

**Monolithic single-file Flask app.** Everything lives in `main.py` (~295 lines):

- **No ORM** — raw `sqlite3` with parameterized queries
- **No Blueprints** — all routes on a single `app` object
- **No app factory** pattern
- **No migrations tool** — schema changes require manual DB edits or new `init_db()` logic
- **Secret key is hardcoded** (`"your-secret-key-change-this-in-production"`)
- **`finance.db` is committed to git** and contains real data

### Routes

| Route | Method | Auth | Purpose |
|-------|--------|------|---------|
| `/login` | GET/POST | No | Login page |
| `/logout` | GET | Yes | Logout |
| `/` | GET | Yes | Dashboard with line chart |
| `/add` | POST | Yes | Add financial record |
| `/data` | GET | Yes | JSON API: per-user daily totals |
| `/records` | GET | Yes | CRUD table, filter by date |
| `/update` | POST | Yes | Update a record |
| `/delete/<id>` | POST | Yes | Delete a record |
| `/account-data` | GET | Yes | JSON API: per-user-account time series |
| `/pie-chart` | GET | Yes | Pie chart page |
| `/pie-data` | GET | Yes | JSON API: user & account proportions on latest date |

### Database Schema

```sql
CREATE TABLE records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    user TEXT,
    account TEXT,
    amount REAL
);

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT              -- werkzeug hashed
);
```

Default user: `admin` / `admin123` (auto-created on first `init_db()`).

## Code Conventions

From AGENTS.md:

- **PEP 8** style, 4-space indentation, **120-char max line length**
- **snake_case** for variables/functions, **PascalCase** for classes, **UPPER_SNAKE_CASE** for constants
- **Type hints** for function parameters and return values
- **Import order**: stdlib → third-party → local, alphabetically within each group
- **Database operations**: always use parameterized queries, use context managers or ensure connections are closed, commit after writes
- **Error handling**: try/except for DB operations, return appropriate HTTP status codes
- **Templates**: keep logic minimal, pass only necessary data, use Bootstrap classes

## Adding Features

1. Add route in `main.py`
2. Add template in `templates/` if needed
3. Test manually (no automated test suite exists)
4. Follow DB error handling patterns (see AGENTS.md for examples)

## Package Manager

**uv is canonical** (has `uv.lock`, Dockerfile uses `uv sync --frozen`). `requirements.txt` exists as a legacy fallback. Build backend is Hatchling.
