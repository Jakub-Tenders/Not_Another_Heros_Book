# Not Another Hero's Book

An interactive "Choose Your Own Adventure" storytelling app built with Flask (REST API) and Django (frontend), connected via HTTP with two separate PostgreSQL databases.

EPITA Python for Web — Project by Jakub, Tristan

---

## Architecture

```
Browser
  |
Django (localhost:8000)
|-- PostgreSQL: mohith_rpg      <- users, sessions, ratings, reports
|-- HTTP requests
        |
        Flask API (localhost:5001)
        |-- PostgreSQL: storyline       <- stories, pages, choices
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
Tables created
Mohith story imported successfully!
```

---

## 4. Django Setup

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

## 5. Create a Superuser (Admin Account)

To access admin moderation features (suspend stories, review reports), create a superuser:

```bash
cd mohith_rpg
source ../venv/bin/activate
python manage.py createsuperuser
```

You will be prompted to enter:
- Username (e.g. `admin`)
- Email address (can be left blank, just press Enter)
- Password (must be at least 8 characters and not too common)

This account will have `is_staff = True`, which gives it access to the Admin nav link, the story moderation panel, and the reports panel.

To create a regular Author account, register through the web UI at `http://127.0.0.1:8000/accounts/register/` and then promote it to Author role via the Django admin panel at `http://127.0.0.1:8000/admin/`.

---

## 6. Running the Project

You need two terminals open at the same time.

Terminal 1 — Flask API:
```bash
source venv/bin/activate
cd flask_api
python app.py
# Running on http://127.0.0.1:5001
```

Terminal 2 — Django:
```bash
source venv/bin/activate
cd mohith_rpg
python manage.py runserver
# Running on http://127.0.0.1:8000
```

Then open `http://127.0.0.1:8000` in your browser.

---

## 7. Test Accounts and Feature Walkthrough

The following sections describe how to test every major feature of the application.

### Anonymous Reader (no login required)

1. Visit `http://127.0.0.1:8000`
2. You will see the published stories list. The seeded story "Mohith's Python Exam Adventure" should appear.
3. Use the search bar to filter stories by title.
4. Click "Play" on a story to begin.
5. Make choices using the buttons. The session is tracked automatically via a UUID session key in the URL.
6. Reach an ending — you will see the ending label (e.g. "The End") and options to play again or return home.
7. If you close the browser mid-story and return to the same session URL, your progress is saved (PlaySession record).

### Registered Reader Account

1. Visit `http://127.0.0.1:8000/accounts/register/` and create an account.
2. You will be logged in automatically and redirected to the home page.
3. Play a story while logged in — the Play record will be linked to your user account.
4. Visit `http://127.0.0.1:8000/accounts/profile/` to see your role (Reader by default).
5. Logout via the navbar link.

### Author Account

To become an Author, either:
- Create a superuser as described above and use the Django admin panel to edit a user's `UserProfile` and set `role = author`, or
- Register a new user, log in as your superuser, go to `http://127.0.0.1:8000/admin/`, find the UserProfile for that user, and change their role to `author`.

Once you have an Author account:

1. Login at `http://127.0.0.1:8000/accounts/login/`
2. The navbar will show an "Author Tools" link.
3. Visit `http://127.0.0.1:8000/author/` to see your Author Dashboard.
4. Click "+ New Story" to create a story. Fill in title, description, tags, and set status to Draft or Published.
5. After creating, you are taken to the story edit page. Click "+ Add Page" to add pages.
6. On the page creation form, write the page text. Tick "This is an ending page" if applicable and optionally add an Ending Label.
7. After saving a page, click "Edit" on it to add choices. Each choice requires a text label and a destination page.
8. To connect pages into a story, add choices linking one page to the next. The start page is set automatically when the first page is created.
9. Change the story status to "Published" to make it visible in the public list.
10. Use the "Preview" button on the story edit page to play it before publishing.
11. To delete a page or choice, use the Delete buttons — a confirmation dialog will appear.
12. To delete a story, use the Delete button on the Author Dashboard — a confirmation dialog will appear.

### Admin Account

Use the superuser account created in step 5.

1. Login at `http://127.0.0.1:8000/accounts/login/` with your superuser credentials.
2. The navbar will show both "Author Tools" and "Admin" links.
3. Visit `http://127.0.0.1:8000/admin/stories/` to see all stories across all authors.
4. Click "Suspend" next to a story to change its status to `suspended`. It will disappear from the public list and players will be blocked from starting it.
5. Click "Unsuspend" to restore it to published.
6. Visit `http://127.0.0.1:8000/admin/reports/` to see user-submitted reports.
7. Click "Review" on a report to see the details. You can suspend the reported story or dismiss the report, and optionally add moderator notes.

### API Key Protected Endpoints

Write operations on the Flask API require the `X-API-KEY` header. To test this manually:

```bash
# This should succeed (public read endpoint)
curl http://127.0.0.1:5001/stories

# This should fail with 401 (missing key)
curl -X POST http://127.0.0.1:5001/stories -H "Content-Type: application/json" -d '{"title": "Test"}'

# This should succeed (correct key)
curl -X POST http://127.0.0.1:5001/stories \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: your-secret-key-here" \
  -d '{"title": "Test Story", "description": "A test", "author_name": "Me"}'
```

Replace `your-secret-key-here` with the value from your `.env` file.

---

## 8. Verify Flask API Connection from Django Shell

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
|
|-- flask_api/                   # Story content REST API
|   |-- app.py                   # Flask entry point (port 5001)
|   |-- models.py                # Story, Page, Choice models
|   |-- routes.py                # All API endpoints
|   |-- config.py                # Loads .env config
|   |-- import_story.py          # Seeds the database with story data
|   |-- requirements.txt
|   |-- .env                     # not committed to git
|
|-- mohith_rpg/                  # Django frontend
    |-- manage.py
    |-- .env                     # not committed to git (goes here, next to manage.py)
    |-- static/
    |   |-- css/style.css
    |-- templates/
    |   |-- base.html
    |   |-- home.html
    |   |-- play.html
    |   |-- author/
    |   |   |-- dashboard.html
    |   |   |-- story_form.html
    |   |   |-- story_edit.html
    |   |   |-- page_form.html
    |   |   |-- choice_form.html
    |   |-- registration/
    |   |   |-- login.html
    |   |   |-- register.html
    |   |   |-- profile.html
    |   |-- admin/
    |       |-- stories.html
    |       |-- reports.html
    |       |-- report_review.html
    |-- mohith_rpg/              # Django project config
    |   |-- settings.py
    |   |-- urls.py
    |-- game/                    # Main Django app
        |-- models.py            # Play, PlaySession, UserProfile, Rating, Report
        |-- views.py             # Gameplay and author views
        |-- views_auth.py        # Auth and admin moderation views
        |-- urls.py              # URL routing
        |-- flask_api.py         # HTTP client for Flask API
        |-- decorators.py        # story_owner_required decorator
        |-- migrations/
```

---

## Flask API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/health` | No | Health check |
| GET | `/stories` | No | List stories (`?status=`, `?search=`, `?tags=`) |
| GET | `/stories/<id>` | No | Get story (`?include_pages=true` for full tree) |
| GET | `/stories/<id>/start` | No | Get starting page ID |
| GET | `/pages/<id>` | No | Get page with its choices |
| POST | `/stories` | Yes | Create story |
| PUT | `/stories/<id>` | Yes | Update story |
| DELETE | `/stories/<id>` | Yes | Delete story and all its pages and choices |
| POST | `/stories/<id>/pages` | Yes | Add page to story |
| PUT | `/pages/<id>` | Yes | Update page |
| DELETE | `/pages/<id>` | Yes | Delete page |
| POST | `/pages/<id>/choices` | Yes | Add choice to page |
| PUT | `/choices/<id>` | Yes | Update choice |
| DELETE | `/choices/<id>` | Yes | Delete choice |

Write endpoints require the header: `X-API-KEY: your-secret-key-here`

---

## Django Pages

| URL | Description |
|-----|-------------|
| `/` | Home — browse published stories |
| `/play/<id>/` | Start a story |
| `/play/session/<key>/` | Read current page and make choices |
| `/play/session/<key>/choice/<id>/` | Submit a choice |
| `/play/<id>/restart/` | Restart a story |
| `/author/` | Author dashboard |
| `/author/stories/create/` | Create a new story |
| `/author/stories/<id>/edit/` | Edit story and manage pages |
| `/author/stories/<id>/delete/` | Delete a story |
| `/author/stories/<id>/pages/create/` | Add a page |
| `/author/pages/<id>/edit/` | Edit page and manage choices |
| `/author/pages/<id>/delete/` | Delete a page |
| `/author/pages/<id>/choices/create/` | Add a choice |
| `/author/choices/<id>/delete/` | Delete a choice |
| `/accounts/register/` | Register new account |
| `/accounts/login/` | Login |
| `/accounts/logout/` | Logout |
| `/accounts/profile/` | View your profile |
| `/admin/stories/` | Admin — moderate all stories |
| `/admin/stories/<id>/suspend/` | Suspend a story |
| `/admin/stories/<id>/unsuspend/` | Unsuspend a story |
| `/admin/reports/` | Admin — view all reports |
| `/admin/reports/<id>/review/` | Review and resolve a report |

---

## Grading Level Assessment

This project targets Level 16/20.

Level 10 (MVP) — complete. Stories can be created, edited, and published. Pages and choices form a navigable tree. Anonymous Play records are saved when an ending is reached.

Level 13 (Advanced gameplay) — complete. Search and filter on the home page. Named ending labels shown on the end screen. PlaySession model provides auto-save per session key. Draft vs. published visibility is enforced. Confirmation dialogs on destructive actions.

Level 16 (Security and roles) — complete. Django auth with register/login/logout. UserProfile with Reader, Author, and Admin roles. Author tools require login via `@login_required`. Story edit and delete require ownership via `story_owner_required` decorator. Flask write endpoints protected with `X-API-KEY`. Admins can suspend and unsuspend stories.

Level 18 (Ratings and reports) — partial. The Rating and Report models are defined in Django. The admin can view and action reports. User-facing views to submit ratings or reports are not yet implemented. Story tree visualization, player path visualization, illustrations, and random events are not implemented.

---

## Common Issues

`Error fetching stories: API Error: HTTP 403`
Flask API is not running. Start it in Terminal 1 first.

`Port 5000 conflict on Mac`
macOS uses port 5000 for AirPlay Receiver. This app uses port 5001 to avoid the conflict.

`ENV LOADED - FLASK_API_URL = http://localhost:5000`
The `.env` file is in the wrong location. It must be at `mohith_rpg/.env`, not `mohith_rpg/mohith_rpg/.env`.

`django.db.utils.OperationalError: could not connect to server`
PostgreSQL is not running. Start it with `brew services start postgresql` (macOS) or `sudo service postgresql start` (Linux).