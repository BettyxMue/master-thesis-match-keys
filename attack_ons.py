import pandas as pd
import re
import hashlib

# Load the original dataset for attribute distribution analysis
df_original = pd.read_csv("known-german_healthcare_records_500.csv")
df_ons = pd.read_csv("matchkey-output-500_ons.csv")

# Analyze top distributions for key fields used in ONS and Randall tokens
top_first_names = df_original["first_name"].value_counts().head(10).index.tolist()
top_last_names = df_original["last_name"].value_counts().head(10).index.tolist()
top_dobs = df_original["dob"].value_counts().head(10).index.tolist()
top_yobs = df_original["year_of_birth"].value_counts().head(10).index.astype(str).tolist()
top_zips = df_original["zip"].value_counts().head(10).index.tolist()
top_genders = df_original["gender"].value_counts().head(2).index.tolist()
top_emails = df_original["email"].value_counts().head(10).index.tolist()
top_addresses = df_original["address"].value_counts().head(10).index.tolist()
top_first_initials = df_original["first_initial"].value_counts().head(10).index.tolist()

# Helper functions
def normalize(s):
    return re.sub(r'\W+', '', str(s).lower().strip()) if pd.notnull(s) else ""

def hash_fields(fields):
    combined = "".join(normalize(f) for f in fields if f)
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()

# Attack mk1 (first + last + dob)
guessed_ons_mk1 = {
    hash_fields([fn, ln, dob])
    for fn in top_first_names
    for ln in top_last_names
    for dob in top_dobs
}

# Attack mk2 (first_initial + last + dob)
guessed_ons_mk2 = {
    hash_fields([fi, ln, dob])
    for fi in top_first_initials
    for ln in top_last_names
    for dob in top_dobs
}

# mk3 = first + zip + dob
guessed_ons_mk3 = {
    hash_fields([fn, zipc, dob])
    for fn in top_first_names
    for zipc in top_zips
    for dob in top_dobs
}

# mk4 = soundex(last_name) + dob
def soundex_simple(name):
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
    return (code + "000")[:4]

guessed_ons_mk4 = {
    hash_fields([soundex_simple(ln), dob])
    for ln in top_last_names
    for dob in top_dobs
}

# mk5 = first[:3] + last + year_of_birth
guessed_ons_mk5 = {
    hash_fields([fn[:3], ln, yob])
    for fn in top_first_names
    for ln in top_last_names
    for yob in top_yobs
}

# Compare to actual match keys
ons_mk1_hits = df_ons["mk1"].isin(guessed_ons_mk1).sum()
ons_mk2_hits = df_ons["mk2"].isin(guessed_ons_mk2).sum()
ons_mk3_hits = df_ons["mk3"].isin(guessed_ons_mk3).sum()
ons_mk4_hits = df_ons["mk4"].isin(guessed_ons_mk4).sum()
ons_mk5_hits = df_ons["mk5"].isin(guessed_ons_mk5).sum()

ons_attack_results = {
        "mk1_hits": ons_mk1_hits,
        "mk2_hits": ons_mk2_hits,
        "mk3_hits": ons_mk3_hits,
        "mk4_hits": ons_mk4_hits,
        "mk5_hits": ons_mk5_hits
    }

print(ons_attack_results)