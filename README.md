# Codveda Python Developer Internship

This repository holds my completed work for the **Python Development** internship at **Codveda Technologies**, a remote internship that is my first internship experience.

The internship has three levels (Basic, Intermediate, Advanced). Each level offers three tasks, and I complete two tasks per level. Python is also a key skill for my path into cybersecurity, where it is used to automate tasks and write scripts.

**Author:** Yoreka Albert, GitHub: [yorekadeve](https://github.com/yorekadeve)

---

## Repository structure

```
codveda-python-internship/
├── level_1_basic/                  Level 1 (Basic)
│   ├── Calculator.py        Task 1: Simple Calculator
│   ├── word_counter.py      Task 3: Word Counter
│   └── sample.txt           Sample text file for the Word Counter
├── Level_2_Intermediate/        Level 2 (Intermediate)
│   ├── data_scraper.py          Task 2: Data Scraper
│   └── api_integration.py       Task 3: Password Breach Checker (API integration)
├── Level_3_Advanced/            Level 3 (Advanced)
│   ├── (Django project)         Task 1: ScamShield UG, Django web application
│   └── file_encryption/         Task 2: File Encryption and Decryption application
└── README.md
```

Each level has its own folder, and each task is its own Python file.

---

## Level 1 (Basic)

I completed two tasks:

1. **Task 1: Simple Calculator**
2. **Task 3: Word Counter**

### Task 1: Simple Calculator (`level_1_basic/calculator.py`)

**What it does:** asks the user for two numbers and an operation (`+`, `-`, `*`, `/`), then prints the result.

**How I built it:**
- Wrote one function for each operation: `add`, `subtract`, `multiply` and `divide`.
- A `calculator()` function takes two inputs and lets the user choose the operation, then uses `if / elif / else` to call the matching function.
- The `divide` function checks for zero first and returns a clear error message instead of crashing.
- Used `try / except ValueError` so that typing letters instead of numbers gives a friendly error.

**How to run it:**
```
python level_1_basic/calculator.py
```

**Example:**
```
Enter the first number: 10
Enter the second number: 5
Choose an operation (+, -, *, /): +
Result: 15.0
```

### Task 3: Word Counter (`level_1_basic/word_counter.py`)

**What it does:** reads a text file and counts the number of words in it.

**How I built it:**
- A `count_words()` function opens the file in read mode using a `with` statement, so the file closes automatically.
- It reads the content, uses `split()` to cut the text into words, and `len()` to count them.
- A `main()` function asks for the file path and uses `try / except` to handle a missing file (`FileNotFoundError`), a file without permission (`PermissionError`), and a file that is not text (`UnicodeDecodeError`).

**How to run it:**
```
python level_1_basic/word_counter.py
```
When asked for the file path, enter `level_1_basic/sample.txt` (included in the repo).

**Example:**
```
Enter the path of the text file: level1/sample.txt
The file contains 13 word(s).
```

### What I learned in Level 1

- Writing and calling functions, and keeping each function to one job
- Taking user input and converting it to the right type
- Making decisions with `if / elif / else`
- Reading files safely with `with open(...)`
- Handling errors with `try / except` so programs fail gracefully

---

## Requirements

- Python 3
- No extra packages need to be installed.

---

## Level 2 (Intermediate)

### Task 2: Data Scraper (`Level_2_Intermediate/data_scraper.py`)

**What it does:** downloads the first page of [books.toscrape.com](https://books.toscrape.com/), a practice website built for learning web scraping, extracts the title and price of each of the 20 books, and saves them to a CSV file.

**How I built it:**
- `requests.get()` retrieves the page, with a timeout so the program never waits forever, and `raise_for_status()` raises an error if the site answers with a failure.
- `BeautifulSoup` parses the HTML. Each book sits in an `article` tag with the class `product_pod`, so `find_all()` returns one item per book.
- The title is read from the link's `title` attribute, because the visible text is cut short on long titles. The price is read from the `price_color` paragraph.
- `csv.DictWriter` saves the results to `books.csv`, with a `title,price` header. The file uses `utf-8-sig` encoding so the `£` sign displays correctly in Excel.
- A `try / except requests.exceptions.RequestException` handles download failures (no internet, timeout, bad status) with a clear message, and a check handles a page that loads with no books found.

**How to run it:**
```
pip install requests beautifulsoup4
python Level_2_Intermediate/data_scraper.py
```
The program creates `books.csv` in the `Level_2_Intermediate` folder each time it runs.

**Example output:**
```
Scraped 20 books and saved them to books.csv
```

**Example rows in `books.csv`:**
```
title,price
A Light in the Attic,£51.77
Tipping the Velvet,£53.74
```

### Task 3: API Integration, Password Breach Checker (`Level_2_Intermediate/api_integration.py`)

**What it does:** checks whether a password has appeared in known data breaches, using the free [Have I Been Pwned Pwned Passwords API](https://haveibeenpwned.com/API/v3#PwnedPasswords). It needs no API key.

**Security design:** the password is typed with hidden input, hashed locally with SHA-1, and only the first 5 characters of the hash are sent to the API (a technique called k-anonymity). The API returns every hash that starts with those 5 characters, and the match is checked on my own computer, so the password itself is never sent.

**How I built it:**
- `getpass.getpass()` reads the password without showing it on screen, and `hashlib.sha1()` creates the hash.
- `requests.get()` sends a GET request with only the 5-character prefix, with a timeout, and `raise_for_status()` raises an error on a failure response.
- The response is plain text with one `SUFFIX:COUNT` line per hash. The program splits each line, compares the suffix with the rest of my hash, and reads the breach count.
- The result is shown as a clear warning with the number of breaches, or a message that the password was not found.
- A `try / except / else` block handles a timeout, no internet connection, a failure response from the server, and an unexpected response format.

**How to run it:**
```
python Level_2_Intermediate/api_integration.py
```
Typing is hidden, so nothing appears as the password is entered. Use dummy passwords only, never real ones.

**Example output (with a common password):**
```
=== Password Breach Checker ===
Your password is never sent. Only the first 5 characters of its hash are.
Enter a password to check (typing is hidden):
WARNING: This password appeared 2,266,677 times in known data breaches. Do not use it.
```

### What I learned in Level 2

- Sending HTTP requests with the `requests` library and handling network errors such as timeouts and lost connections
- Parsing HTML with BeautifulSoup and picking out data by tag and class
- Writing structured data to a CSV file with Python's `csv` module
- Scraping responsibly, by practising on a website designed for it
- Using a public API and parsing its text response
- Applying security ideas in code: hashing, k-anonymity, and hidden password input

## Requirements

- Python 3
- Level 1 needs no extra packages.
- Level 2 needs `requests` and `beautifulsoup4`:
  pip install requests beautifulsoup4
---

## Level 3 (Advanced)

### Task 1: Django Web Application with Authentication, ScamShield UG (`Level_3_Advanced/`)

**What it does:** a community scam-reporting and checking portal for Uganda. Anyone can check a phone number or link before paying. Registered users report scams and confirm other users' reports. Moderators verify or reject reports. The public sees only verified results, and never the reporter, the description or the screenshot.

**How I built it:**
- **Authentication:** Django's built-in system handles registration, login, logout and password reset by email. Passwords are hashed, and reset links work once and expire after an hour.
- **Roles:** visitors, registered users, moderators (a group holding a custom `review_reports` permission) and admins. Every protected page checks the role on the server.
- **Database:** MySQL, through a database user limited to this project. Secrets are kept in a `.env` file that is never committed.
- **Reports and checker:** phone numbers and links are normalised, so different spellings of the same number match. Screenshots are checked for size, extension and real image format, saved under random names, and served only to the owner and moderators.
- **Security layer:** login lockout after 5 failed attempts, rate limits, a read-only audit log, CSRF and XSS protection, secure cookie and HTTPS settings, and separation of duties so moderators cannot approve their own reports.
- **Statistics and confirmations:** a public statistics page built from verified reports, and a "I was also targeted by this" button that moderators see as a count in the queue.
- **Tests:** 51 automated tests prove the security rules.

**How to run it:**
```
cd Level_3_Advanced
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
The database and the `.env` file must be set up first. The full steps are in [Level_3_Advanced/README.md](Level_3_Advanced/README.md). To run the tests:
```
python manage.py test --noinput
```

**Example result for a verified number:**
```
Verified scam
This number or link has been reported and verified 2 times. Do not send money or share personal details.
Checked as: +256772123456
```

### Task 2: Basic File Encryption/Decryption (`Level_3_Advanced/file_encryption/file_encryption.py`)

**What it does:** encrypts a text file with a password and saves it as a new file ending in `.enc`, then decrypts it back to the original text in another new file. The original file is never overwritten.

**How I built it:**
- I used Fernet from the `cryptography` library instead of a Caesar cipher, because Fernet is real encryption: AES with an authentication code, so a wrong password or a modified file is detected and refused.
- The key is never typed directly. The password is turned into a 256-bit key with PBKDF2-HMAC-SHA256 (600,000 rounds) and a random 16-byte salt, so the same password gives a different key for every file and guessing passwords is slow.
- The encrypted file stores a short header and the salt, followed by the encrypted data, so decrypting needs only the file and the password.
- The user chooses to encrypt or decrypt and enters the file path. The password is typed with hidden input, and when encrypting it must be at least 8 characters and typed twice.
- Errors are handled with clear messages: file not found, wrong password or changed file, a file not encrypted by this program, and an output file that already exists.
- 8 unit tests check the round trip, wrong passwords, tampering, and that the encrypted file never contains the plain text.

**How to run it:**
```
pip install cryptography
python Level_3_Advanced/file_encryption/file_encryption.py
```
To run the tests:
```
python -m unittest discover -s Level_3_Advanced/file_encryption -v
```

**Example:**
```
=== File Encryption and Decryption ===
1. Encrypt a file
2. Decrypt a file
Choose 1 or 2: 1
Enter the path of the file: Level_3_Advanced/file_encryption/sample_secret.txt
Choose a password (typing is hidden):
Type the password again:
Encrypted. Saved as: Level_3_Advanced\file_encryption\sample_secret.txt.enc
```
### What I learned in Level 3

- Building a complete Django application with models, views, forms, templates and URLs
- Role-based access control with groups and permissions
- Defending against common web attacks: IDOR, CSRF, XSS, SQL injection, brute-force login, unsafe file upload, and scraping
- Keeping secrets out of code, and applying least privilege to the database
- Writing automated tests that prove security rules keep working
- Encrypting and decrypting files with Fernet, and why real encryption beats a Caesar cipher
- Deriving encryption keys from passwords with a salt and PBKDF2
- Authenticated encryption: detecting wrong passwords and tampered files
---
### Requirements
- Level 3, Task 2 needs `cryptography`: `pip install cryptography`
