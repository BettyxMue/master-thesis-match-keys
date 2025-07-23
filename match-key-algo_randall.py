import hashlib
import random
from faker import Faker
import pandas as pd
import re

# Initialize Faker for German locale
fake = Faker("de_DE")
Faker.seed(42)
random.seed(42)

# Helper to normalize strings
def normalize(s):
    return re.sub(r'\W+', '', s.lower().strip()) if s else ""

# Generate SHA-256 hash of concatenated, normalized fields
def hash_fields(fields):
    combined = "".join(normalize(f) for f in fields if f)
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()

# Improved Randall-style match key algorithm (2021 version with better QID mixing)
def randall_improved_match_keys(record):
    qid_sets = [
        ["first_name", "last_name", "dob"],
        ["first_name", "zip", "year_of_birth"],
        ["last_name", "dob", "gender"],
        ["first_name", "gender", "zip"],
        ["first_name", "last_name", "email"],
        ["last_name", "year_of_birth", "zip"],
        ["first_initial", "last_name", "dob"],
        ["first_name", "address", "zip"],
        ["first_name", "dob", "email"],
        ["last_name", "gender", "email"]
    ]
    
    match_keys = {}
    for i, qids in enumerate(qid_sets):
        values = [record.get(qid, "") for qid in qids]
        match_keys[f"mk_randall_{i+1}"] = hash_fields(values)
    
    return match_keys

# Sample test record
record = {
    "first_name": "Anna",
    "last_name": "Schmidt",
    "dob": "1985-06-23",
    "year_of_birth": "1985",
    "zip": "10115",
    "gender": "F",
    "email": "anna.schmidt@example.de",
    "address": "Berliner Straße 123",
    "first_initial": "A"
}

# Generate and display improved Randall match keys
randall_keys = randall_improved_match_keys(record)
randall_keys
