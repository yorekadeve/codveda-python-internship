import getpass
import hashlib

import requests

API_URL = "https://api.pwnedpasswords.com/range/"

#Password used for demonstartion: password123
def hash_password(password):
    return hashlib.sha1(password.encode("utf-8")).hexdigest().upper()

#Technique used here is - k-anonymity
def fetch_hash_range(prefix):
    response = requests.get(API_URL + prefix, timeout=10)
    response.raise_for_status()
    return response.text


def count_breaches(hash_suffix, api_response):
    for line in api_response.splitlines():
        suffix, _, count = line.partition(":")
        if suffix == hash_suffix:
            return int(count)
    return 0


def check_password(password):
    full_hash = hash_password(password)
    prefix, suffix = full_hash[:5], full_hash[5:]
    api_response = fetch_hash_range(prefix)
    return count_breaches(suffix, api_response)


def main():
    print("=== Password Breach Checker ===")
    print("Your password is never sent. Only the first 5 characters of its hash are.")
    password = getpass.getpass("Enter a password to check (typing is hidden): ")

    if not password:
        print("Error: Please enter a password.")
        return

    try:
        breaches = check_password(password)
    except requests.exceptions.Timeout:
        print("Error: The request timed out. Try again.")
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect. Check your internet connection.")
    except requests.exceptions.HTTPError as error:
        print(f"Error: The server returned a failure response. {error}")
    except ValueError:
        print("Error: The server sent a response in an unexpected format.")
    else:
        if breaches:
            print(f"WARNING: This password appeared {breaches:,} times in known data breaches. Do not use it.")
        else:
            print("Not found in known breaches. That does not make it strong, so still use a long, unique password.")


if __name__ == "__main__":
    main()