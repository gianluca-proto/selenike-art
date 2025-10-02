# Selenike Art

Selenike Art is a portfolio/showcase website for the artist Selenike, built with Flask (Python) and Bootstrap. The project includes: an image gallery, a commissions page, an artist biography page, a contact form, an admin panel for managing uploads and syncing with Cloudinary, and several security features (JWT-based authentication, CSRF protection, rate limiting and reCAPTCHA).

This README is intended as a presentation document to show on GitHub: it contains the information needed to run, test and evaluate the project.

---

Table of contents
- Description
- Technologies
- Main features
- Project architecture
- Requirements
- Local installation
- Important environment variables
- Running in development
- Migrations and database
- Tests
- Security and best practices implemented
- Deployment (Heroku / Gunicorn)
- How to showcase the project on GitHub
- Contributing
- License
- Contact

---

Description

A showcase website to promote Selenike's artworks and commission services. It provides a responsive user experience, media asset management (Cloudinary) and admin tools to keep the gallery up to date.

Technologies
- Python 3.10+ (compatible with 3.12)
- Flask 3
- Flask-SQLAlchemy, Flask-Migrate
- Flask-WTF (form validation + CSRF)
- Argon2 for password hashing
- PyJWT for JWT tokens
- Cloudinary for media management
- Flask-Babel for localization
- Flask-Limiter for rate limiting
- Flask-Compress, Flask-Caching
- APScheduler for periodic jobs (logs sync)

Main features
- Informational homepage
- Image gallery with category filters
- Commissions page with a request form
- Contact form for email messages
- Protected admin area (JWT + refresh tokens)
- Upload, move and delete images on Cloudinary
- Periodic synchronization of logs and CSV files to Cloudinary
- reCAPTCHA protection for admin login
- Access logging (access.log) for simple monitoring

Project architecture (summary)
- `app.py`: application creation and configuration, blueprint registration, job scheduler
- `config.py`: central configuration and helper functions (e.g. `validate_image`)
- `routes/`: blueprints for public pages and admin (main.py, admin.py, gallery.py, security.py)
- `models/`: SQLAlchemy models (Admin, RefreshToken, etc.)
- `services/`: business logic and integrations (auth, cloudinary, email, security)
- `templates/`: Jinja2 templates for each page
- `static/`: CSS/JS/images
- `migrations/`: Alembic migration scripts

Requirements
- Python 3.10 or newer
- pip
- A PostgreSQL database (local or remote) or a valid `DATABASE_URL` string
- Cloudinary account (optional, for media features)

Local quick installation

1) Clone the repository

```bash
git clone <repo-url>
cd selenike-art
```

2) Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

3) Install dependencies

```bash
pip install -r requirements.txt
```

Important environment variables
Create a `.env` file in the project root with the main environment variables. Example:

```env
APP_SECRET_KEY=a_long_random_string
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

Notes:
- If `DATABASE_URL` is not set, `config.py` uses a default connection string intended for a local Postgres instance.
- For local development you may temporarily set `SESSION_COOKIE_SECURE=False` if you don't use HTTPS (see README warnings).

Migrations and database

1) Create initial migrations (if you need to apply DB changes):

```bash
flask db init   # only the first time (if migrations/ is empty)
flask db migrate -m "Initial migration"
flask db upgrade
```

(A `migrations/` folder with at least one migration is included in the project.)

Running in development

Quick method (run `app.py` directly):

```bash
python app.py
```

Or with the Flask CLI (if `FLASK_APP` is set):

```bash
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
```

For running with Gunicorn (production or Heroku):

```bash
gunicorn --bind 0.0.0.0:8000 app:app
```

Tests

The project contains some tests in the `tests/` folder. To run them:

```bash
pip install -r requirements.txt
pytest -q
```

Security (implemented choices)
- Password hashing: Argon2 (see `GenerateHashPassword.py` for a hash example)
- CSRF protection: Flask-WTF + CSRFProtect
- Token-based auth: JWT for the admin area, with refresh token support (`RefreshToken` model)
- reCAPTCHA: used on the admin login to reduce bots and brute-force
- Rate limiting: Flask-Limiter on sensitive routes
- Security headers: Content-Security-Policy, X-Frame-Options, X-Content-Type-Options, X-XSS-Protection are set in `app.py`
- Secure cookies: session and auth cookies are set HttpOnly, Secure and SameSite (in `config.py` and the admin routes)

Deployment (quick notes)
- A `Procfile` for Heroku is included.
- Example steps for Heroku:
  - Set the config vars on Heroku (all the environment variables listed above)
  - Push the repository and scale the web dyno
  - Ensure `DATABASE_URL` points to a managed Postgres instance

How to showcase the project on GitHub
- Add screenshots of the homepage, gallery and admin panel to a `docs/` folder or the repository root.
- Create a `DEMO.md` file with links (if the site is deployed) and a short walkthrough.
- Use the README to highlight: features, the tech stack, screenshots and quick start instructions.
- Optionally add a short video (GIF or MP4) in `docs/` showing the flow: gallery view → commission request → admin login → image upload (Cloudinary).

Practical tips for the repo presentation:
- Update the "Description" section with a short note about your role and what you implemented (e.g. "Implemented JWT authentication, Cloudinary integration and reCAPTCHA protections").
- Add CI badges (tests/coverage) if you enable CI
- Add a license badge

Contributing
- Open issues for bugs or feature requests
- Fork & pull request: create a branch for your feature and open a descriptive PR

License
- The project can be released under the MIT license (or another license you prefer). Add a `LICENSE` file to make it explicit.

Contact
- Managed by Gianluca Proto
- For live demos or questions, add an email or contact link in the README (optional).

---

Current status and final notes
- The code already contains Cloudinary integration, a synchronization job, i18n support (Flask-Babel) and several security improvements.
- If you want, I can also add to the repository:
  - a `.env.example` file
  - deployment scripts
  - additional unit tests for service functions (Cloudinary, auth)

If you want me to also create a `README_de.md` or other language versions, a `DEMO.md`, or add `.env.example`/`LICENSE`/CI, tell me which ones and I will add them.
