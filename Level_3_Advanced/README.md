# ScamShield UG

A community-powered web application for checking and reporting scam phone numbers, links and messages in Uganda. Built with Django and MySQL as Level 3, Task 1 of the Codveda Python Developer internship.

## The problem

Scams through mobile money and fake SMS messages are widely reported in Uganda, and most victims have no quick way to check a number or link before they send money. ScamShield UG lets anyone check before they pay, and lets the community report what they see.

## Features

- **Public scam checker:** anyone can search a phone number or link. Numbers are normalised, so `0772 123 456` and `+256772123456` match. The answer is one of three: verified scam, reported but not yet verified, or no reports found. A site-wide report also covers every page of that site.
- **Accounts:** registration, login, logout and password reset by email. Reset links work once and expire after one hour.
- **Reporting:** logged-in users report a number or link with a description, the scam message, the amount lost, the date, and an optional screenshot.
- **Community confirmations:** users can click "I was also targeted by this", once per report, never on their own report.
- **Moderation queue:** moderators review pending reports, with the most-confirmed first, and verify them or reject them with a reason. They also see other reports of the same number or link.
- **Statistics page:** verified reports, numbers and links flagged, reported losses, scams by type, most reported numbers and links, and incidents by month.
- **Audit log:** a read-only record of logins, failed logins, lockouts, reports, moderator decisions and screenshot views, with IP addresses.

## User roles

| Role | What they can do |
|------|------------------|
| Visitor | Check numbers and links, view statistics |
| Registered user | Everything above, plus submit reports, track their own reports, and confirm reports |
| Moderator | Everything above, plus review and verify or reject reports, and view screenshots. Cannot review their own report |
| Admin | Everything above, plus manage users and groups, and read the audit log in the Django admin |

Moderators are users in the `Moderators` group, which holds the custom `review_reports` permission.

## Security measures

- Passwords hashed by Django (PBKDF2 with a salt), with a 10-character minimum and common-password checks
- Secrets (`SECRET_KEY`, database password) read from a `.env` file that is never committed
- Separate MySQL user limited to this project's database
- CSRF protection on every form, and logout only by POST
- Django's automatic output escaping (XSS) and ORM queries (SQL injection)
- Server-side role checks on every protected page, so hiding a button is never the only protection
- Protection against users opening other people's reports or screenshots (IDOR): they receive a 404
- Screenshots served only through a permission-checking view, never from a public folder
- Upload checks: file size (2 MB), file extension, and the real image format, and files stored under random names
- Only verified reports are shown publicly. Reporter identities, descriptions and screenshots are never public
- Login lockout after 5 failed attempts per IP and username, for 15 minutes
- Rate limits on search, registration, password reset, reporting and confirming
- Password reset that never reveals whether an email has an account
- Separation of duties: moderators cannot approve their own reports
- Secure cookie, HTTPS and HSTS settings that switch on when `DEBUG` is off (`manage.py check --deploy` reports no issues)
- Automated tests that prove these rules

## Tech stack

Python, Django 5.2, MySQL 8, Pillow, Bootstrap 5 (CDN), python-dotenv.

## Setup (Windows, PowerShell)

1. Clone the repository and open a PowerShell window in it.
2. Create and activate a virtual environment:
   ```
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
3. Install the requirements:
   ```
   cd Level_3_Advanced
   pip install -r requirements.txt
   ```
4. In MySQL, create the database and a limited user:
   ```sql
   CREATE DATABASE scamshield CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   CREATE USER 'scamshield_user'@'localhost' IDENTIFIED BY 'choose-a-strong-password';
   GRANT ALL PRIVILEGES ON scamshield.* TO 'scamshield_user'@'localhost';
   GRANT ALL PRIVILEGES ON test_scamshield.* TO 'scamshield_user'@'localhost';
   ```
5. Copy `.env.example` to `.env` and fill in a secret key and the database password:
   ```
   Copy-Item .env.example .env
   ```
   A secret key can be generated with:
   ```
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```
6. Create the tables and an admin account:
   ```
   python manage.py migrate
   python manage.py createsuperuser
   ```
7. Start the site and open http://127.0.0.1:8000/:
   ```
   python manage.py runserver
   ```
8. To create moderators, open `/admin/`, add a group named `Moderators` with the permission "Can review scam reports", and add users to it.

## Running the tests

```
python manage.py test --noinput
```

The tests build a temporary database, so real data is never touched.

## Project structure

```
Level_3_Advanced/
├── config/          Settings and main URL routes
├── accounts/        Registration, login with lockout, password reset
├── reports/         Reports, checker, confirmations, moderation, statistics
├── audit/           Audit log, signals and the rate limiter
├── templates/       Shared layout and pages
├── requirements.txt
└── .env.example
```

## Production notes

- Counters for rate limiting and lockout are kept in server memory. A deployment with several servers would use a shared cache such as Redis.
- Client IP addresses are read from the direct connection. Behind a reverse proxy, the proxy settings must be configured.
- Emails are printed to the terminal in development. A real deployment needs SMTP settings.
- The `/admin/` login uses Django's own form, so the superuser needs a strong password.