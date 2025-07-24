import hashlib
import pandas as pd
import random
from faker import Faker
import re
import json
import sys


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

# ONS-style match key generation for a DataFrame
def generate_ons_match_keys(df):
    df["mk1"] = df.apply(lambda row: hash_fields([row["first_name"], row["last_name"], row["dob"]]), axis=1)
    df["mk2"] = df.apply(lambda row: hash_fields([row["first_initial"], row["last_name"], row["dob"]]), axis=1)
    df["mk3"] = df.apply(lambda row: hash_fields([row["first_name"], row["zip"], row["dob"]]), axis=1)
    df["mk4"] = df.apply(lambda row: hash_fields([soundex_simple(row["last_name"]), row["dob"]]), axis=1)
    df["mk5"] = df.apply(lambda row: hash_fields([row["first_name"][:3] if pd.notnull(row["first_name"]) else "", row["last_name"], row["year_of_birth"]]), axis=1)
    return df

# Create a test record
""" record = {
    "first_name": "Anna",
    "last_name": "Schmidt",
    "dob": "1985-06-23",
    "year_of_birth": "1985",
    "postcode": "10115",
    "first_initial": "A"
} """

# Generate and show ONS-style match keys
""" match_keys = ons_match_keys(record)
print(json.dumps(match_keys, indent=4)) """ 

# Fix the normalize function to handle float inputs (e.g., NaN) robustly
def normalize(s):
    try:
        return re.sub(r'\W+', '', str(s).lower().strip()) if pd.notnull(s) else ""
    except Exception:
        return ""
    
# Reload and reprocess the dataset
df_input = pd.read_csv("german_healthcare_records_500.csv")
df_with_keys = generate_ons_match_keys(df_input)

# Keep only the match key columns in the output
match_key_columns = ["mk1", "mk2", "mk3", "mk4", "mk5"]
df_keys_only = df_with_keys[match_key_columns]

# Save to a new CSV
keys_only_csv_path = "matchkey-output-500_ons.csv"
df_keys_only.to_csv(keys_only_csv_path, index=False)