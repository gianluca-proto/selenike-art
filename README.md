# 🎨 Selenike Art — Artist Portfolio Website (Flask + Bootstrap + Cloudinary)

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-red)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5-purple)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue)
![License: MIT](https://img.shields.io/badge/License-MIT-green)

Selenike Art is a modern, responsive portfolio website built with **Flask (Python)** and **Bootstrap** to showcase the artworks, commissions, and biography of the artist **Selenike**.  
The project includes an image gallery, commissions page, contact form, and a full admin panel for uploading and managing artworks through **Cloudinary**, secured with **JWT authentication**, **CSRF protection**, **rate limiting**, and **reCAPTCHA**.

This README provides everything needed to run, test, present, and evaluate the project.

---

## 📑 Table of Contents

- Description  
- Technologies  
- Key Features  
- Project Architecture  
- Requirements  
- Local Installation  
- Environment Variables  
- Development Run  
- Migrations & Database  
- Testing  
- Security & Best Practices  
- Deployment (Heroku / Gunicorn)  
- How to Present This Project  
- Contributing  
- License  
- Contact  

---

## 🖼️ Description

Selenike Art is a portfolio website designed to promote the artworks and commission services of the artist **Selenike**.  
It features a responsive interface, Cloudinary-based media management, and an admin dashboard to keep the gallery updated efficiently and securely.

---

## 🛠 Technologies

- **Python 3.10+**  
- **Flask 3**  
- Flask-SQLAlchemy  
- Flask-Migrate  
- Flask-WTF (validation + CSRF)  
- Argon2 (password hashing)  
- PyJWT (access & refresh tokens)  
- Cloudinary (media management)  
- Flask-Babel (i18n)  
- Flask-Limiter (rate limiting)  
- Flask-Compress, Flask-Caching  
- APScheduler (cron-like jobs)

---

## 🌐 Key Features

- Responsive homepage  
- Dynamic image gallery with category filters  
- Commission request form  
- Contact form via email  
- **Admin panel with JWT + refresh token system**  
- Upload / rename / delete artworks on Cloudinary  
- Scheduled sync of logs & CSV files  
- reCAPTCHA-protected admin login  
- Access logging (access.log)  

---

## 📂 Project Architecture

```
app.py               → Flask initialization, blueprints, scheduler
config.py            → Central configuration + utilities
routes/              → Public/admin routes (main, admin, gallery, security)
models/              → SQLAlchemy ORM models
services/            → Business logic (auth, media, email, security)
templates/           → Jinja2 HTML templates
static/              → CSS / JS / images
migrations/          → Alembic migration scripts
tests/               → Automated tests
docs/                → Screenshots and demo materials
```

---

## 📌 Requirements

- Python 3.10+  
- pip  
- PostgreSQL  
- Cloudinary account (optional)  

---

## 🧪 Local Installation (Quick Start)

### 1) Clone the repository

```bash
git clone <repo-url>
cd selenike-art
```

### 2) Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3) Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🔐 Environment Variables

Create a `.env` file in the project root:

```env
APP_SECRET_KEY=your_secret_key
DATABASE_URL=postgresql://user:password@localhost/selenike_art
MAIL_SERVER=smtp.example.com
MAIL_PORT=587
MAIL_USERNAME=user@example.com
MAIL_PASSWORD=secret
RECAPTCHA_SITE_KEY=your_site_key
RECAPTCHA_SECRET_KEY=your_secret_key
CLOUD_NAME=your_cloud_name
CLOUD_API_KEY=your_api_key
CLOUD_API_SECRET=your_api_secret
```

**Notes:**  
- If `DATABASE_URL` is missing, `config.py` uses a default Postgres URI.  
- For localhost without HTTPS, set `SESSION_COOKIE_SECURE=False`.

---

## 🗄️ Migrations & Database

If initializing migrations:

```bash
flask db init   # only once
flask db migrate -m "Initial migration"
flask db upgrade
```

A full `migrations/` folder is already included.

---

## ▶️ Run in Development

### Using app.py directly:

```bash
python app.py
```

### Using Flask CLI:

```bash
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
```

### With Gunicorn (production-like):

```bash
gunicorn --bind 0.0.0.0:8000 app:app
```

---

## 🧪 Testing

```bash
pytest -q
```

---

## 🔒 Security & Best Practices

- **Argon2** password hashing  
- **JWT authentication** (access + refresh)  
- **CSRF protection**  
- **reCAPTCHA** for admin login  
- **Rate limiting** via Flask-Limiter  
- **Security headers:**  
  - Content-Security-Policy  
  - X-Frame-Options  
  - X-Content-Type-Options  
  - X-XSS-Protection  
- **Secure cookies:** HttpOnly, Secure, SameSite  
- Input validation (forms, images, MIME types)

---

## ☁️ Deployment (Heroku)

This project includes a `Procfile`.

### Deployment steps:

1. Set environment variables in Heroku  
2. Push the repository  
3. Scale the `web` dyno  
4. Attach PostgreSQL  
5. Run migrations  

---

## 🎥 How to Present / Demo This Project

- Add screenshots inside the `docs/` folder  
- Add a `DEMO.md` walkthrough  
- Optionally include a GIF demonstrating:
  - Gallery → Commission → Admin login → Image upload  
- Add badges (license, build, tests)

### Highlight your contributions:

- JWT authentication  
- Cloudinary integration  
- Anti-bot protections (reCAPTCHA + rate limiting)  
- Secure cookies  
- APScheduler jobs  

---

## 🤝 Contributing

- Open issues for bugs or feature requests  
- Fork and submit PRs  
- Use feature branches  

---

## 📄 License

Distributed under the **MIT License**.  
Add a `LICENSE` file for full details.

---

## 📬 Contact

**Developer:** Gianluca Proto  
**Email:** gianlucaproto@gmail.com  
**LinkedIn:** https://www.linkedin.com/in/gianluca-proto-a4031a269/

