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

---