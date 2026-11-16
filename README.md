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
│   └── data_scraper.py          Task 2: Data Scraper
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

### What I learned in Level 2 so far

- Sending HTTP requests with the `requests` library and handling network errors
- Parsing HTML with BeautifulSoup and picking out data by tag and class
- Writing structured data to a CSV file with Python's `csv` module
- Scraping responsibly, by practising on a website designed for it