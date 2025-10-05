# FastAPI Todo App with Auth (Render Ready)

A full-stack todo app with user registration/login, JWT auth, and PostgreSQL.

## Features
- User registration & login
- Create, edit (toggle), delete todos
- Secure password hashing
- Cookie-based JWT auth
- Responsive HTML/CSS/JS frontend

## Deploy to Render
1. Push this code to a GitHub repo
2. Go to [Render Dashboard](https://dashboard.render.com/)
3. Click **New + → Blueprint**
4. Connect your repo
5. Render auto-deploys with DB + web service

> `render.yaml` handles everything: DB provisioning, env vars (`DATABASE_URL`, `SECRET_KEY`), and startup.

## Local Development
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload