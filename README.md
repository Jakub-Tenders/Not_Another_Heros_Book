# Not Another Hero's Book 

An interactive "Choose Your Own Adventure" storytelling app built with **Flask** (REST API) and **Django** (frontend), connected via HTTP with two separate PostgreSQL databases.

> **EPITA Python for Web — Project by Jakub, Tristan **

---

## Architecture

```
Browser
  ↓
Django (localhost:8000)
├── PostgreSQL: mohith_rpg      ← users, sessions, ratings, reports
└── HTTP requests
        ↓
Flask API (localhost:5001)
└── PostgreSQL: storyline       ← stories, pages, choices
```

---

## Requirements

- Python 3.10+
- PostgreSQL (running locally)
- One shared virtual environment (or two separate ones)

---

## 1. PostgreSQL Setup

Open `psql` and create the two databases:

```sql
CREATE DATABASE storyline;
CREATE DATABASE mohith_rpg;
```

---

## 2. Virtual Environment

```bash
python -m venv venv
source venv/bin/activate
pip install flask flask-sqlalchemy flask-cors psycopg2-binary python-dotenv django requests
```

---

## 3. Flask API Setup

```bash
cd flask_api
```

Create the file `flask_api/.env`:
```
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/storyline
FLASK_API_KEY=your-secret-key-here
```

Import the story data into the database:
```bash
python import_story.py
```

You should see:
```
✓ Tables created
✓ Mohith story imported successfully!
```

---

## 4. Django Frontend Setup

```bash
cd mohith_rpg
```

Create the file `mohith_rpg/.env` (next to `manage.py`):
```
FLASK_API_URL=http://localhost:5001
FLASK_API_KEY=your-secret-key-here
```

 The `FLASK_API_KEY` must be identical in both `.env` files.

Run database migrations:
```bash
python manage.py migrate
```

---

## 5. Running the Project

You need **two terminals open at the same time**.

**Terminal 1 — Flask API:**
```bash
source venv/bin/activate
cd flask_api
python app.py
# → Running on http://127.0.0.1:5001
```

**Terminal 2 — Django:**
```bash
source venv/bin/activate
cd mohith_rpg
python manage.py runserver
# → Running on http://127.0.0.1:8000
```

Then open **http://127.0.0.1:8000** in your browser.

---

## 6. Verify Everything Works

```bash
source venv/bin/activate
cd mohith_rpg
python manage.py shell
```

```python
from game.flask_api import flask_api
stories = flask_api.get_stories()
print(stories)   # Should show Mohith's Python Exam Adventure
```

---

## Project Structure

```
Not_Another_Heros_Book/
│
├── flask_api/                   # Story content REST API
│   ├── app.py                   # Flask entry point (port 5001)
│   ├── models.py                # Story, Page, Choice models
│   ├── routes.py                # All API endpoints
│   ├── config.py                # Loads .env config
│   ├── import_story.py          # Seeds the database with story data
│   ├── requirements.txt
│   └── .env                     # ← not committed to git
│
└── mohith_rpg/                  # Django frontend
    ├── manage.py
    ├── .env                     # ← not committed to git (goes here, next to manage.py)
    ├── static/
    │   └── css/style.css
    ├── templates/
    │   ├── base.html
    │   ├── home.html
    │   ├── play.html
    │   └── author/
    │       ├── dashboard.html
    │       ├── story_form.html
    │       ├── story_edit.html
    │       ├── page_form.html
    │       └── choice_form.html
    ├── mohith_rpg/              # Django project config
    │   ├── settings.py
    │   └── urls.py
    └── game/                    # Main Django app
        ├── models.py            # Play, PlaySession, UserProfile, Rating, Report
        ├── views.py             # All view functions
        ├── urls.py              # URL routing
        ├── flask_api.py         # HTTP client for Flask API
        └── migrations/
```

---

## Flask API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|:----:|-------------|
| GET | `/health` | — | Health check |
| GET | `/stories` | — | List stories (`?status=`, `?search=`, `?tags=`) |
| GET | `/stories/<id>` | — | Get story (`?include_pages=true` for full tree) |
| GET | `/stories/<id>/start` | — | Get starting page ID |
| GET | `/pages/<id>` | — | Get page with its choices |
| POST | `/stories` | ✓ | Create story |
| PUT | `/stories/<id>` | ✓ | Update story |
| DELETE | `/stories/<id>` | ✓ | Delete story + all pages + choices |
| POST | `/stories/<id>/pages` | ✓ | Add page to story |
| PUT | `/pages/<id>` | ✓ | Update page |
| DELETE | `/pages/<id>` | ✓ | Delete page |
| POST | `/pages/<id>/choices` | ✓ | Add choice to page |
| PUT | `/choices/<id>` | ✓ | Update choice |
| DELETE | `/choices/<id>` | ✓ | Delete choice |

Write endpoints require the header: `X-API-KEY: your-secret-key-here`

---

## Django Pages

| URL | Description |
|-----|-------------|
| `/` | Home — browse published stories |
| `/play/<id>/` | Start a story |
| `/play/session/<key>/` | Read current page and make choices |
| `/author/` | Author dashboard |
| `/author/stories/create/` | Create a new story |
| `/author/stories/<id>/edit/` | Edit story and manage pages |
| `/author/pages/<id>/edit/` | Edit page and manage choices |

---

## Common Issues

**`Error fetching stories: API Error: HTTP 403`**
Flask API is not running. Start it in Terminal 1 first.

**Port 5000 conflict on Mac**
we found that mac uses port 5000 for AirPlay Receiver. This app uses port **5001** to avoid the conflict.

**`ENV LOADED - FLASK_API_URL = http://localhost:5000`**
The `.env` file is in the wrong place. It must be at `mohith_rpg/.env`, not `mohith_rpg/mohith_rpg/.env`.
