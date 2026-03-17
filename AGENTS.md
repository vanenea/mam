# Agent Guidelines for MAM (Financial Records Management)

## Project Overview

MAM is a Flask-based web application for managing financial records. It uses SQLite for data storage and provides a simple UI for tracking user expenses across different accounts.

## Project Structure

```
mam/
├── main.py              # Flask application and routes
├── requirements.txt     # Python dependencies
├── templates/           # HTML templates
│   ├── base.html
│   ├── index.html
│   └── records.html
├── static/              # Static assets
│   ├── css/
│   └── js/
├── finance.db           # SQLite database
└── AGENTS.md            # This file
```

## Build & Run Commands

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run the Application
```bash
python main.py
```
The app runs on `http://0.0.0.0:5000` in debug mode.

### Run with Flask CLI
```bash
FLASK_APP=main.py flask run
```

## Testing

No tests currently exist in this project. When adding tests:

### Run All Tests
```bash
pytest
# or
python -m pytest
```

### Run a Single Test
```bash
pytest tests/test_file.py::test_function_name
# or
python -m pytest tests/test_file.py::test_function_name
```

### Run Tests with Coverage
```bash
pytest --cov=. --cov-report=html
```

## Code Style Guidelines

### General Conventions
- Follow PEP 8 style guide
- Use 4 spaces for indentation
- Maximum line length: 120 characters
- Use descriptive variable and function names

### Imports
- Standard library imports first
- Third-party imports second
- Local imports last
- Alphabetically ordered within each group
- Example:
  ```python
  import sqlite3
  from datetime import datetime
  
  from flask import Flask, render_template, request, redirect, jsonify
  ```

### Type Hints
- Add type hints for function parameters and return values
- Use `Optional` for nullable types
- Example:
  ```python
  def get_record(record_id: int) -> Optional[dict]:
      ...
  ```

### Naming Conventions
- Variables and functions: `snake_case` (e.g., `get_data`, `record_id`)
- Classes: `PascalCase` (e.g., `FinancialRecord`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `DB_NAME`)
- Routes: lowercase with hyphens (e.g., `/account-data`)

### Error Handling
- Use try/except blocks for database operations
- Always close database connections (use context managers)
- Return appropriate HTTP status codes
- Example:
  ```python
  try:
      conn = sqlite3.connect(DB_NAME)
      c = conn.cursor()
      # ... operations
  except sqlite3.Error as e:
      return jsonify({"error": str(e)}), 500
  finally:
      if conn:
          conn.close()
  ```
- Or use context manager:
  ```python
  with sqlite3.connect(DB_NAME) as conn:
      c = conn.cursor()
      # ... operations
  ```

### Database Operations
- Use parameterized queries to prevent SQL injection
- Always commit after write operations
- Use context managers for connections

### Routes
- Use appropriate HTTP methods (GET, POST, PUT, DELETE)
- Put route decorators directly above route functions
- Use `/<int:record_id>` for path parameters

### Templates
- Keep templates simple; minimize logic in templates
- Pass only necessary data from routes
- Use Bootstrap classes for styling (already included)

### Flask Best Practices
- Use `request.args` for query parameters (GET)
- Use `request.form` for form data (POST)
- Return appropriate responses (render_template, jsonify, redirect)

## Adding New Features

1. Add route in `main.py`
2. Add corresponding template in `templates/` if needed
3. Test the new route manually
4. Ensure database operations follow error handling guidelines

## Database Schema

```sql
CREATE TABLE records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    user TEXT,
    account TEXT,
    amount REAL
);
```

## Common Tasks

### Add a New Route
```python
@app.route("/new-route", methods=["GET", "POST"])
def new_route():
    if request.method == "POST":
        # handle form submission
        return redirect("/")
    return render_template("new_template.html")
```

### Query Database
```python
with sqlite3.connect(DB_NAME) as conn:
    c = conn.cursor()
    c.execute("SELECT * FROM records WHERE user=?", (user,))
    rows = c.fetchall()
```

### Return JSON
```python
return jsonify({"key": "value"})
```

## Notes

- Debug mode is enabled in development (`debug=True`)
- Database file: `finance.db` in project root
- The app uses ECharts for data visualization on the index page