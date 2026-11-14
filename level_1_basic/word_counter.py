# ===== LEVEL 1 - TASK 3: WORD COUNTER =====

def count_words(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
    words = content.split()
    return len(words)


def main():
    print("=== Word Counter ===")
    file_path = input("Enter the path of the text file: ").strip().strip('"')

    try:
        total = count_words(file_path)
        print(f"The file contains {total} word(s).")
    except FileNotFoundError:
        print("Error: File not found. Check the file name and path, then try again.")
    except PermissionError:
        print("Error: You do not have permission to read this file.")
    except UnicodeDecodeError:
        print("Error: This file is not a readable text file.")


if __name__ == "__main__":
    main()