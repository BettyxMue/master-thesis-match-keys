import hashlib
import pandas as pd
import random
from faker import Faker
import re

# Initialize Faker for German locale
fake = Faker("de_DE")
Faker.seed(42)
random.seed(42)

# Normalize strings
def normalize(s):
    return re.sub(r'\W+', '', s.lower().strip()) if s else ""

# Phonetic encoding (simplified Soundex-like for demonstration)
def soundex_simple(name):
    name = normalize(name)
    if not name:
        return ""
    code = name[0].upper()
    mappings = {"bfpv": "1", "cgjkqsxz": "2", "dt": "3", "l": "4", "mn": "5", "r": "6"}
    for char in name[1:]:
        for key, value in mappings.items():
            if char in key:
                if value != code[-1]:  # avoid duplicates
                    code += value
    return (code + "000")[:4]

# Generate hash
def hash_fields(fields):
    combined = "".join(normalize(f) for f in fields if f)
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()

# ONS-style match keys
def ons_match_keys(record):
    return {
        "mk1": hash_fields([record["first_name"], record["last_name"], record["dob"]]),
        "mk2": hash_fields([record["first_initial"], record["last_name"], record["dob"]]),
        "mk3": hash_fields([record["first_name"], record["postcode"], record["dob"]]),
        "mk4": hash_fields([soundex_simple(record["last_name"]), record["dob"]]),
        "mk5": hash_fields([record["first_name"][:3], record["last_name"], record["year_of_birth"]])
    }

# Create a test record
record = {
    "first_name": "Anna",
    "last_name": "Schmidt",
    "dob": "1985-06-23",
    "year_of_birth": "1985",
    "postcode": "10115",
    "first_initial": "A"
}

# Generate and show ONS-style match keys
match_keys = ons_match_keys(record)
match_keys
