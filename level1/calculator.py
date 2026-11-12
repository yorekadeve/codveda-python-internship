# ===== LEVEL 1 - TASK 1: SIMPLE CALCULATOR =====

def add(a, b):
    return a + b


def subtract(a, b):
    return a - b


def multiply(a, b):
    return a * b


def divide(a, b):
    if b == 0:
        return "Error: Division by zero is not allowed."
    return a / b


def calculator():
    print("=== Simple Calculator ===")
    print("Operations: + (add), - (subtract), * (multiply), / (divide)")

    try:
        num1 = float(input("Enter the first number: "))
        num2 = float(input("Enter the second number: "))
    except ValueError:
        print("Error: Please enter valid numbers only.")
        return

    operation = input("Choose an operation (+, -, *, /): ")

    if operation == "+":
        result = add(num1, num2)
    elif operation == "-":
        result = subtract(num1, num2)
    elif operation == "*":
        result = multiply(num1, num2)
    elif operation == "/":
        result = divide(num1, num2)
    else:
        print("Error: Invalid operation. Use +, -, * or /.")
        return

    print("Result:", result)


calculator()