# 🎨 Selenike Art — Artist Portfolio Website (Flask + Bootstrap + Cloudinary)

Selenike Art is a modern, responsive portfolio website built with **Flask (Python)** and **Bootstrap** to showcase the artworks, commissions, and biography of the artist **Selenike**.  
The project includes an image gallery, a commissions page, a contact form, an admin panel for media management (upload/sync via Cloudinary), and multiple security features such as JWT authentication, CSRF protection, rate limiting, and reCAPTCHA.

This document serves as the official README for GitHub and provides all essential information to run, test, evaluate, and present the project.

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
- Security Features  
- Deployment (Heroku / Gunicorn)  
- How to Present This Project  
- Contributing  
- License  
- Contacts  

---

## 🖼️ Description

Selenike Art is a portfolio website designed to showcase the artworks and commission services of the artist *Selenike*.  
It provides a fully responsive user experience, Cloudinary-based media management, and an administrative interface to keep the gallery updated.

---

## 🛠 Technologies

- **Python 3.10+** (compatible with 3.12)
- **Flask 3**
- **Flask-SQLAlchemy**, **Flask-Migrate**
- **Flask-WTF** (validation + CSRF)
- **Argon2** (password hashing)
- **PyJWT** (JWT authentication)
- **Cloudinary** (media storage/management)
- **Flask-Babel** (localization)
- **Flask-Limiter** (rate limiting)
- **Flask-Compress**, **Flask-Caching**
- **APScheduler** (scheduled tasks)

---

## 🌐 Key Features

- Responsive homepage  
- Image gallery with category filters  
- Commission request page  
- Contact form (email)  
- **Admin dashboard with JWT authentication + refresh tokens**  
- Upload / rename / delete images on Cloudinary  
- Automatic sync of logs and CSV files (APScheduler)  
- reCAPTCHA-protected admin login  
- Access logging (access.log)  

---

## 📂 Project Architecture (Overview)

- **app.py:** Flask app creation, configuration, blueprints, scheduler  
- **config.py:** central configuration, helpers (e.g., `validate_image`)  
- **routes/**: blueprints for public and admin pages (`main.py`, `admin.py`, `gallery.py`, `security.py`)  
- **models/**: SQLAlchemy models (`Admin`, `RefreshToken`, etc.)  
- **services/**: business logic and integrations (auth, Cloudinary, email, security)  
- **templates/**: Jinja2 templates  
- **static/**: CSS/JS/Image assets  
- **migrations/**: Alembic migration scripts  

---

## 📌 Requirements

- Python 3.10+  
- pip  
- PostgreSQL (local or remote)  
- Cloudinary account (optional for media functions)  

---

## 🧪 Local Installation (Quick Start)

### 1) Clone the repository

```bash
git clone <repo-url>
cd selenike-art
2) Create and activate a virtual environment
bash
Copia codice
python -m venv .venv
source .venv/bin/activate
3) Install dependencies
bash
Copia codice
pip install -r requirements.txt
🔐 Important Environment Variables
Create a .env file in the project root:

env
Copia codice
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
Notes:

If DATABASE_URL is missing, config.py will fall back to a default local Postgres string.

For local development without HTTPS, set SESSION_COOKIE_SECURE=False.

🗄️ Migrations & Database
If migrations need to be initialized:

bash
Copia codice
flask db init   # only once
flask db migrate -m "Initial migration"
flask db upgrade
The current project already includes a migrations/ folder.

▶️ Run in Development
Using app.py directly:

bash
Copia codice
python app.py
Using Flask CLI:

bash
Copia codice
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
With Gunicorn (local production / Heroku):

bash
Copia codice
gunicorn --bind 0.0.0.0:8000 app:app
🧪 Testing
Tests are located in tests/.

Run with:

bash
Copia codice
pytest -q
🔒 Security & Best Practices Implemented
Argon2 hashing for passwords

JWT authentication with refresh tokens

CSRF protection via Flask-WTF

reCAPTCHA for admin login

Rate limiting with Flask-Limiter

Security headers:

Content-Security-Policy

X-Frame-Options

X-Content-Type-Options

X-XSS-Protection

Secure cookies: HttpOnly, Secure, SameSite

Input validation (forms, images, mime types)

☁️ Deployment (Heroku)
The project includes a Procfile.

Deployment steps:

Set environment variables in Heroku

Push the repository

Scale the web dyno

Attach a managed PostgreSQL database

Run migrations

🎥 How to Present / Demo This Project on GitHub
Add screenshots (homepage, gallery, admin panel) to a docs/ folder

Add a DEMO.md file with walkthrough and (optional) demo links

Use the README to highlight tech stack, screenshots, and installation steps

Optionally add a GIF showing workflow:

Viewing gallery → Commission form → Admin login → Image upload

Add badges:

tests coverage

license

Tips for highlighting your work:

Mention your implementations:

JWT authentication

Cloudinary integration

reCAPTCHA anti-bot protections

secure cookies

scheduler jobs

🤝 Contributing
Open issues for bugs or feature requests

Fork the repo and submit PRs

Use separate branches for each feature

📄 License
This project can be released under MIT (recommended).
Add a LICENSE file to explicitly declare it.

📬 Contact
Developer: Gianluca Proto
Email: gianlucaproto@gmail.com
LinkedIn: https://www.linkedin.com/in/gianluca-proto-a4031a269/
