import re
from urllib.parse import urlparse


def normalize_phone(value):
    value = value.strip()
    international = value.startswith("+") or value.startswith("00")
    digits = re.sub(r"\D", "", value)
    if value.startswith("00"):
        digits = digits[2:]

    if international:
        return "+" + digits if 8 <= len(digits) <= 15 else None
    if digits.startswith("0") and len(digits) == 10:
        return "+256" + digits[1:]
    if digits.startswith("256") and len(digits) == 12:
        return "+" + digits
    if len(digits) == 9:
        return "+256" + digits
    return None


def normalize_link(value):
    value = value.strip().lower()
    if "://" not in value:
        value = "http://" + value
    try:
        parsed = urlparse(value)
        host = parsed.hostname
    except ValueError:
        return None
    if not host or "." not in host:
        return None
    host = host.removeprefix("www.")
    return host + parsed.path.rstrip("/")


def normalize_indicator(indicator_type, value):
    if indicator_type == "phone":
        return normalize_phone(value) or ""
    if indicator_type == "link":
        return normalize_link(value) or ""
    return value.strip().lower()