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

def find_hit_combinations(df, column_name, guessed_dict):
    matched = []
    for h in df[column_name]:
        if h in guessed_dict:
            matched.append((h, guessed_dict[h]))
    return matched

# Attack mk_randall_1 (first + last + dob)
guessed_randall_mk1 = {
    hash_fields([fn, ln, dob]): (fn, ln, dob)
    for fn in top_first_names
    for ln in top_last_names
    for dob in top_dobs
}

matches_mk1 = find_hit_combinations(df_randall, "mk_randall_1", guessed_randall_mk1)

# Attack mk_randall_2 (first + zip + yob)
guessed_randall_mk2 = {
    hash_fields([fn, zipc, yob]): (fn, zipc, yob)
    for fn in top_first_names
    for zipc in top_zips
    for yob in top_yobs
}
matches_mk2 = find_hit_combinations(df_randall, "mk_randall_2", guessed_randall_mk2)

# mk_randall_3 = last_name + dob + gender
guessed_randall_mk3 = {
    hash_fields([ln, dob, g]): (ln, dob, g)
    for ln in top_last_names
    for dob in top_dobs
    for g in top_genders
}

matches_mk3 = find_hit_combinations(df_randall, "mk_randall_3", guessed_randall_mk3)

# mk_randall_4 = first_name + gender + zip
guessed_randall_mk4 = {
    hash_fields([fn, g, zipc]): (fn, g, zipc)
    for fn in top_first_names
    for g in top_genders
    for zipc in top_zips
}

matches_mk4 = find_hit_combinations(df_randall, "mk_randall_4", guessed_randall_mk4)

# mk_randall_5 = first + last + email
guessed_randall_mk5 = {
    hash_fields([fn, ln, email]): (fn, ln, email)
    for fn in top_first_names
    for ln in top_last_names
    for email in top_emails
}

matches_mk5 = find_hit_combinations(df_randall, "mk_randall_5", guessed_randall_mk5)

# mk_randall_6 = last + yob + zip
guessed_randall_mk6 = {
    hash_fields([ln, yob, zipc]): (ln, yob, zipc)
    for ln in top_last_names
    for yob in top_yobs
    for zipc in top_zips
}

matches_mk6 = find_hit_combinations(df_randall, "mk_randall_6", guessed_randall_mk6)

# mk_randall_7 = first_initial + last + dob
guessed_randall_mk7 = {
    hash_fields([fi, ln, dob]): (fi, ln, dob)
    for fi in top_first_initials
    for ln in top_last_names
    for dob in top_dobs
}

matches_mk7 = find_hit_combinations(df_randall, "mk_randall_7", guessed_randall_mk7)

# mk_randall_8 = first_name + address + zip
guessed_randall_mk8 = {
    hash_fields([fn, addr, zipc]): (fn, addr, zipc)
    for fn in top_first_names
    for addr in top_addresses
    for zipc in top_zips
}

matches_mk8 = find_hit_combinations(df_randall, "mk_randall_8", guessed_randall_mk8)

# mk_randall_9 = first_name + dob + email
guessed_randall_mk9 = {
    hash_fields([fn, dob, email]): (fn, dob, email)
    for fn in top_first_names
    for dob in top_dobs
    for email in top_emails
}

matches_mk9 = find_hit_combinations(df_randall, "mk_randall_9", guessed_randall_mk9)

# mk_randall_10 = last_name + gender + email
guessed_randall_mk10 = {
    hash_fields([ln, g, email]): (ln, g, email)
    for ln in top_last_names
    for g in top_genders
    for email in top_emails
}

matches_mk10 = find_hit_combinations(df_randall, "mk_randall_10", guessed_randall_mk10)

# Evaluate Randall guesses
randall_hits = {
    f"mk_randall_{i+1}": df_randall[f"mk_randall_{i+1}"].isin(eval(f"guessed_randall_mk{i+1}")).sum()
    for i in range(10)
}

print(randall_hits)

if matches_mk1:
    print("Matches for mk_randall_1 (first + last + dob):")
    for hash_val, values in matches_mk1:
        print(f"Hash: {hash_val} ← Values: {values}")

if matches_mk2:
    print("Matches for mk_randall_2 (first + zip + yob):")
    for hash_val, values in matches_mk2:
        print(f"Hash: {hash_val} ← Values: {values}")

if matches_mk3:
    print("Matches for mk_randall_3 (last_name + dob + gender):")
    for hash_val, values in matches_mk3:
        print(f"Hash: {hash_val} ← Values: {values}")

if matches_mk4:
    print("Matches for mk_randall_4 (first_name + gender + zip):")
    for hash_val, values in matches_mk4:
        print(f"Hash: {hash_val} ← Values: {values}")

if matches_mk5:
    print("Matches for mk_randall_5 (first + last + email):")
    for hash_val, values in matches_mk5:
        print(f"Hash: {hash_val} ← Values: {values}")

if matches_mk6:
    print("Matches for mk_randall_6: (last + yob + zip)")
    for hash_val, values in matches_mk6:
        print(f"Hash: {hash_val} ← Values: {values}")

if matches_mk7:
    print("Matches for mk_randall_7: (first_initial + last + dob)")
    for hash_val, values in matches_mk7:
        print(f"Hash: {hash_val} ← Values: {values}")

if matches_mk8:
    print("Matches for mk_randall_8 (first_name + address + zip):")
    for hash_val, values in matches_mk8:
        print(f"Hash: {hash_val} ← Values: {values}")

if matches_mk9:
    print("Matches for mk_randall_9 (first_name + dob + email):")
    for hash_val, values in matches_mk9:
        print(f"Hash: {hash_val} ← Values: {values}")

if matches_mk10:
    print("Matches for mk_randall_10 (last_name + gender + email):")
    for hash_val, values in matches_mk10:
        print(f"Hash: {hash_val} ← Values: {values}")