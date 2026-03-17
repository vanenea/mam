# MAM - Financial Records Management

A Flask-based web application for managing financial records with SQLite database.

## Features

- Add financial records (date, user, account, amount)
- View records with filtering by date
- Update and delete records
- Data visualization with ECharts
- Account-based data analysis

## Quick Start

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run the Application
```bash
python main.py
```

Access the app at `http://localhost:5000`

## Project Structure

```
mam/
├── main.py              # Flask application
├── requirements.txt     # Dependencies
├── templates/           # HTML templates
│   ├── base.html
│   ├── index.html       # Dashboard with charts
│   └── records.html     # Records management
├── static/              # CSS and JS
├── finance.db           # SQLite database
└── README.md
```

## Routes

| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Dashboard with charts |
| `/add` | POST | Add new record |
| `/data` | GET | JSON data for charts |
| `/records` | GET | Records list page |
| `/update` | POST | Update record |
| `/delete/<id>` | POST | Delete record |
| `/account-data` | GET | Account-based data |

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

## Tech Stack

- Flask 3.0.3
- SQLite
- Bootstrap 5
- ECharts