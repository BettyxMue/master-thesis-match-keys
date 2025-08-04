import hashlib
import pandas as pd
import random
from faker import Faker
import re
from jellyfish import soundex

# Initialize Faker for German locale
""" fake = Faker("de_DE")
Faker.seed(42)
random.seed(42) """

# Normalize strings
def normalize(s):
    return re.sub(r'\W+', '', s.lower().strip()) if s else ""

# Phonetic encoding (simplified Soundex-like for demonstration)
""" def soundex_simple(name):
    name = normalize(name)
    if not name:
        return ""
    code = name[0].upper()
    mappings = {"bfpv": "1", "cgjkqsxz": "2", "dt": "3", "l": "4", "mn": "5", "r": "6"}
    for char in name[1:]:
        for key, value in mappings.items():
            if char in key:
                if value != code[-1]:
                    code += value
    return (code + "000")[:4] """

# Generate hash
def hash_fields(fields):
    combined = "".join(normalize(f) for f in fields if f)
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()

# ONS-style match key generation for a DataFrame
def generate_ons_13_matchkeys(df):
    df["dob"] = df["year_of_birth"].apply(lambda y: f"{y}-01-01" if pd.notnull(y) else "")
    df["first_initial"] = df["first_name"].apply(lambda x: x[0] if pd.notnull(x) else "")
    
    df["mk1"] = df.apply(lambda x: hash_fields([x["first_name"], x["last_name"], x["dob"]]), axis=1)
    df["mk2"] = df.apply(lambda x: hash_fields([x["first_name"][0] if pd.notnull(x["first_name"]) else "", x["last_name"], x["dob"]]), axis=1)
    df["mk3"] = df.apply(lambda x: hash_fields([x["first_name"], x["zip"], x["dob"]]), axis=1)
    df["mk4"] = df.apply(lambda x: hash_fields([
        soundex(str(x["last_name"])) if pd.notnull(x["last_name"]) else "", 
        x["dob"]]), axis=1)
    df["mk5"] = df.apply(lambda x: hash_fields([x["first_name"][:3] if pd.notnull(x["first_name"]) else "", x["last_name"], x["year_of_birth"]]), axis=1)
    df["mk6"] = df.apply(lambda x: hash_fields([
        x["first_name"], 
        soundex(str(x["last_name"])) if pd.notnull(x["last_name"]) else "", 
        x["dob"]]), axis=1)
    df["mk7"] = df.apply(lambda x: hash_fields([
        x["first_name"][0] if pd.notnull(x["first_name"]) else "",
        soundex(str(x["last_name"])) if pd.notnull(x["last_name"]) else "",
        x["dob"]]), axis=1)
    df["mk8"] = df.apply(lambda x: hash_fields([x["first_name"], x["last_name"], x["dob"][:7] if pd.notnull(x["dob"]) and len(x["dob"]) >= 7 else ""]), axis=1)
    df["mk9"] = df.apply(lambda x: hash_fields([
        x["first_name"][0] if pd.notnull(x["first_name"]) else "",
        x["last_name"][0] if pd.notnull(x["last_name"]) else "",
        x["year_of_birth"]]), axis=1)
    df["mk10"] = df.apply(lambda x: hash_fields([x["last_name"], x["zip"], x["year_of_birth"]]), axis=1)
    df["mk11"] = df.apply(lambda x: hash_fields([x["first_name"], x["year_of_birth"], x["zip"][:3] if pd.notnull(x["zip"]) else ""]), axis=1)
    df["mk12"] = df.apply(lambda x: hash_fields([
        soundex(str(x["first_name"])) if pd.notnull(x["first_name"]) else "", 
        x["last_name"], 
        x["dob"]]), axis=1)
    df["mk13"] = df.apply(lambda x: hash_fields([x["last_name"], x["year_of_birth"], x["zip"][:3] if pd.notnull(x["zip"]) else ""]), axis=1)
    return df[[f"mk{i}" for i in range(1, 14)]]

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
df_input = pd.read_csv(r"Raw_data/nc_voter_clean_new.csv", dtype="str")
df_with_keys = generate_ons_13_matchkeys(df_input)

# Keep only the match key columns in the output
match_key_columns = ["mk1", "mk2", "mk3", "mk4", "mk5", "mk6", "mk7", "mk8", "mk9", "mk10", "mk11", "mk12", "mk13"]
df_keys_only = df_with_keys[match_key_columns]

# Save to a new CSV
keys_only_csv_path = r"Gen_match_keys/nc_voter_matchkeys_ons.csv"
df_keys_only.to_csv(keys_only_csv_path, index=False)