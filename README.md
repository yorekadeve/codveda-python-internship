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