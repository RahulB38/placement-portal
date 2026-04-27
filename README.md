# Placement Portal Application - V2

Campus recruitment management system for Institutes, Companies, and Students.

## Tech Stack

- **Backend:** Flask, SQLite, Redis, Celery
- **Frontend:** Vue 3, Vite, Bootstrap 5


## Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- Redis
- MailHog 



Run Flask:
```bash
python app.py
```

Run Redis (in another terminal):
```bash
redis-server
```

Run MailHog (in another terminal):
```bash
MailHog   :  .\MailHog_windows_amd64.exe  
Visit : http://localhost:8025/
```

```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Visit http://localhost:5173

## Default Credentials

- **Admin:** admin@placementportal.com / admin123

## Features

- Admin: Approve companies/drives, blacklist, search, statistics
- Company: Register, create drives, manage applications
- Student: Register, apply for drives, view status, export CSV
- Daily email reminders for upcoming deadlines (capturable in MailHog)
- Monthly HTML report to admin (capturable in MailHog)
- CSV export (async via Celery)



# worker
celery -A celery_app worker --loglevel=info --pool=solo

# beat - use same format as worker, without the :celery_app part
celery -A celery_app beat --loglevel=info