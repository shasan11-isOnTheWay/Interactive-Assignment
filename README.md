# Interactive Teaching Platform

A Google Docs-style interactive teaching platform built with Django.

## Features

- **Multi-page editing** — create unlimited pages, each with its own tab in the navbar
- **Rich text editor** — bold, italic, underline, highlight, links, comments, headings, lists
- **Text selection toolbar** — select text to get a floating mini toolbar
- **Comments** — highlight text and add comments; click highlights to view/delete
- **Multimedia section** — upload and manage Text, Image, Audio, Video, YouTube content per page
- **Media modals** — click any media item to view/edit; audio/video have native playback controls
- **Auto-save** — all content saves automatically as you type (1.2s debounce)
- **Expandable sidebar sections** — collapsible sections with editable titles and rich content
- **No login required** — just open and start writing

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run migrations
python manage.py makemigrations
python manage.py migrate

# 3. Start the development server
python manage.py runserver

# 4. Open in browser
# http://localhost:8000/
```

## Project Structure

```
teaching_platform/
├── core/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── editor/
│   ├── models.py          # Page, MultimediaItem, ExpandableSection, Comment
│   ├── views.py           # All views + API endpoints
│   ├── urls.py            # URL routing
│   └── templates/
│       └── editor/
│           └── page.html  # Full single-page app UI
├── media/                 # Uploaded files (auto-created)
├── manage.py
└── requirements.txt
```

## API Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/page/<slug>/` | View/edit a page |
| POST | `/api/page/create/` | Create a new page |
| POST | `/api/page/<slug>/save/` | Save page title/content |
| POST | `/api/page/<slug>/delete/` | Delete a page |
| POST | `/api/page/<slug>/multimedia/add/` | Add multimedia item |
| POST | `/api/multimedia/<id>/save/` | Save multimedia item |
| POST | `/api/multimedia/<id>/upload/` | Replace file |
| POST | `/api/multimedia/<id>/delete/` | Delete multimedia item |
| POST | `/api/page/<slug>/expandable/add/` | Add expandable section |
| POST | `/api/expandable/<id>/save/` | Save expandable section |
| POST | `/api/expandable/<id>/delete/` | Delete expandable section |
| POST | `/api/page/<slug>/comment/add/` | Add comment |
| POST | `/api/comment/<id>/delete/` | Delete comment |

## Notes

- Media files are stored in `media/uploads/`
- Database is SQLite (`db.sqlite3`) — change to PostgreSQL for production
- Secret key should be changed for production deployment
# Interactive-Care-Assignment
