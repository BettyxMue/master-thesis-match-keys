import hashlib
import random
from faker import Faker
import pandas as pd
import re
import json


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
""" def randall_improved_match_keys(record):
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
    
    return match_keys """

# Function to generate Randall-style match keys
def generate_randall_match_keys(df):
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

    for i, qids in enumerate(qid_sets):
        col_name = f"mk_randall_{i+1}"
        df[col_name] = df.apply(lambda row: hash_fields([row.get(qid, "") for qid in qids]), axis=1)
    return df

# Sample test record
""" record = {
    "first_name": "Anna",
    "last_name": "Schmidt",
    "dob": "1985-06-23",
    "year_of_birth": "1985",
    "zip": "10115",
    "gender": "F",
    "email": "anna.schmidt@example.de",
    "address": "Berliner Straße 123",
    "first_initial": "A"
} """

# Generate and display improved Randall match keys
""" randall_keys = randall_improved_match_keys(record)
print(json.dumps(randall_keys, indent=4)) """ 

# Fix the normalize function to handle float inputs (e.g., NaN) robustly
def normalize(s):
    try:
        return re.sub(r'\W+', '', str(s).lower().strip()) if pd.notnull(s) else ""
    except Exception:
        return ""
    
# Load the noisy dataset
df_input = pd.read_csv("german_healthcare_records_500.csv")

# Generate Randall-style match keys
df_with_randall_keys = generate_randall_match_keys(df_input)

# Keep only match key columns
randall_key_columns = [f"mk_randall_{i+1}" for i in range(10)]
df_randall_keys_only = df_with_randall_keys[randall_key_columns]

# Save to CSV
randall_keys_csv_path = "matchkey-output-500_randall.csv"
df_randall_keys_only.to_csv(randall_keys_csv_path, index=False)