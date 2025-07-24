import pandas as pd
import re
import hashlib

# Load the original dataset for attribute distribution analysis
df_original = pd.read_csv("known-german_healthcare_records_500.csv")
df_randall = pd.read_csv("matchkey-output-500_randall.csv")

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

# Attack mk_randall_1 (first + last + dob)
guessed_randall_mk1 = {
    hash_fields([fn, ln, dob])
    for fn in top_first_names
    for ln in top_last_names
    for dob in top_dobs
}

# Attack mk_randall_2 (first + zip + yob)
guessed_randall_mk2 = {
    hash_fields([fn, zipc, yob])
    for fn in top_first_names
    for zipc in top_zips
    for yob in top_yobs
}

# mk_randall_3 = last_name + dob + gender
guessed_randall_mk3 = {
    hash_fields([ln, dob, g])
    for ln in top_last_names
    for dob in top_dobs
    for g in top_genders
}

# mk_randall_4 = first_name + gender + zip
guessed_randall_mk4 = {
    hash_fields([fn, g, zipc])
    for fn in top_first_names
    for g in top_genders
    for zipc in top_zips
}

# mk_randall_5 = first + last + email
guessed_randall_mk5 = {
    hash_fields([fn, ln, email])
    for fn in top_first_names
    for ln in top_last_names
    for email in top_emails
}

# mk_randall_6 = last + yob + zip
guessed_randall_mk6 = {
    hash_fields([ln, yob, zipc])
    for ln in top_last_names
    for yob in top_yobs
    for zipc in top_zips
}

# mk_randall_7 = first_initial + last + dob
guessed_randall_mk7 = {
    hash_fields([fi, ln, dob])
    for fi in top_first_initials
    for ln in top_last_names
    for dob in top_dobs
}

# mk_randall_8 = first_name + address + zip
guessed_randall_mk8 = {
    hash_fields([fn, addr, zipc])
    for fn in top_first_names
    for addr in top_addresses
    for zipc in top_zips
}

# mk_randall_9 = first_name + dob + email
guessed_randall_mk9 = {
    hash_fields([fn, dob, email])
    for fn in top_first_names
    for dob in top_dobs
    for email in top_emails
}

# mk_randall_10 = last_name + gender + email
guessed_randall_mk10 = {
    hash_fields([ln, g, email])
    for ln in top_last_names
    for g in top_genders
    for email in top_emails
}

# Evaluate Randall guesses
randall_hits = {
    f"mk_randall_{i+1}": df_randall[f"mk_randall_{i+1}"].isin(eval(f"guessed_randall_mk{i+1}")).sum()
    for i in range(10)
}

print(randall_hits)