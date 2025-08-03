import pandas as pd
import re
import hashlib

# Define the file paths for the input CSVs
df_original_file = r"Raw_data/nc_voter_clean_dob.csv"
df_ons_file = r"Raw_data/ohio_voter_matchkeys_ons.csv"

# Load the original dataset for attribute distribution analysis
df_original = pd.read_csv(df_original_file)
df_ons = pd.read_csv(df_ons_file)

# Analyze top distributions for key fields used in ONS and Randall tokens
top_first_names = df_original["first_name"].value_counts().head(100).index.tolist()
top_last_names = df_original["last_name"].value_counts().head(100).index.tolist()
top_dobs = df_original["dob"].value_counts().head(100).index.tolist()
top_yobs = df_original["year_of_birth"].value_counts().head(100).index.astype(str).tolist()
top_zips = df_original["zip"].value_counts().head(100).index.tolist()
top_genders = df_original["gender"].value_counts().head(2).index.tolist()
# top_emails = df_original["email"].value_counts().head(100).index.tolist()
top_addresses = df_original["address"].value_counts().head(100).index.tolist()
top_first_initials = df_original["first_initial"].value_counts().head(100).index.tolist()

# Check if the 'email' column exists before analyzing its distribution
if "email" in df_original.columns:
    top_emails = df_original["email"].value_counts().head(100).index.tolist()
else:
    top_emails = []  # Leave it empty if the column doesn't exist

# Helper functions
def normalize(s):
    return re.sub(r'\W+', '', str(s).lower().strip()) if pd.notnull(s) else ""

def hash_fields(fields):
    combined = "".join(normalize(f) for f in fields if f)
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()

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

 # Attack mk1 (first + last + dob)
guessed_ons_mk1 = {
    hash_fields([fn, ln, dob]): (fn, ln, dob)
    for fn in top_first_names
    for ln in top_last_names
    for dob in top_dobs
}

# Find actual hits in df_ons["mk1"]
mk1_matches = []
for hash_val in df_ons["mk1"]:
    if hash_val in guessed_ons_mk1:
        matched_values = guessed_ons_mk1[hash_val]
        mk1_matches.append((hash_val, matched_values))

# Attack mk2 (first_initial + last + dob)
guessed_ons_mk2 = {
    hash_fields([fi, ln, dob]): (fi, ln, dob)
    for fi in top_first_initials
    for ln in top_last_names
    for dob in top_dobs
}

# Find actual hits in df_ons["mk2"]
mk2_matches = []
for hash_val in df_ons["mk2"]:
    if hash_val in guessed_ons_mk2:
        matched_values = guessed_ons_mk2[hash_val]
        mk2_matches.append((hash_val, matched_values))

# mk3 = first + zip + dob
guessed_ons_mk3 = {
    hash_fields([fn, zipc, dob]): (fn, zipc, dob)
    for fn in top_first_names
    for zipc in top_zips
    for dob in top_dobs
}

# Find actual hits in df_ons["mk3"]
mk3_matches = []
for hash_val in df_ons["mk5"]:
    if hash_val in guessed_ons_mk3:
        matched_values = guessed_ons_mk3[hash_val]
        mk3_matches.append((hash_val, matched_values))

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
    hash_fields([soundex_simple(ln), dob]): (ln, dob)
    for ln in top_last_names
    for dob in top_dobs
}

# Find actual hits in df_ons["mk4"]
mk4_matches = []
for hash_val in df_ons["mk4"]:
    if hash_val in guessed_ons_mk4:
        matched_values = guessed_ons_mk4[hash_val]
        mk4_matches.append((hash_val, matched_values))


# mk5 = first[:3] + last + year_of_birth
guessed_ons_mk5 = {
    hash_fields([fn[:3], ln, yob]): (fn, ln, yob)
    for fn in top_first_names
    for ln in top_last_names
    for yob in top_yobs
}

# Find actual hits in df_ons["mk5"]
mk5_matches = []
for hash_val in df_ons["mk5"]:
    if hash_val in guessed_ons_mk5:
        matched_values = guessed_ons_mk5[hash_val]
        mk5_matches.append((hash_val, matched_values))

# mk6 = first + soundex(last_name) + dob
guessed_ons_mk6 = {
    hash_fields([fn, soundex_simple(ln), dob]): (fn, ln, dob)
    for fn in top_first_names
    for ln in top_last_names
    for dob in top_dobs
}

# Find actual hits in df_ons["mk6"]
mk6_matches = []
for hash_val in df_ons["mk6"]:
    if hash_val in guessed_ons_mk6:
        matched_values = guessed_ons_mk6[hash_val]
        mk6_matches.append((hash_val, matched_values))

# mk7 = first_initial + soundex(last_name) + dob
guessed_ons_mk7 = {
    hash_fields([fi, soundex_simple(ln), dob]): (fi, ln, dob)
    for fi in top_first_initials
    for ln in top_last_names
    for dob in top_dobs
}

# Find actual hits in df_ons["mk7"]
mk7_matches = []
for hash_val in df_ons["mk7"]:
    if hash_val in guessed_ons_mk7:
        matched_values = guessed_ons_mk7[hash_val]
        mk7_matches.append((hash_val, matched_values))

# mk8 = first + last + dob[:7]
guessed_ons_mk8 = {
    hash_fields([fn, ln, dob[:7] if pd.notnull(dob) and len(dob) >= 7 else ""]): (fn, ln, dob)
    for fn in top_first_names
    for ln in top_last_names
    for dob in top_dobs
}

# Find actual hits in df_ons["mk8"]
mk8_matches = []
for hash_val in df_ons["mk8"]:
    if hash_val in guessed_ons_mk8:
        matched_values = guessed_ons_mk8[hash_val]
        mk8_matches.append((hash_val, matched_values))

# mk9 = first_initial + last_initial + year_of_birth
guessed_ons_mk9 = {
    hash_fields([fi, ln[0] if pd.notnull(ln) else "", yob]): (fi, ln, yob)
    for fi in top_first_initials
    for ln in top_last_names
    for yob in top_yobs
}

# Find actual hits in df_ons["mk9"]
mk9_matches = []
for hash_val in df_ons["mk9"]:
    if hash_val in guessed_ons_mk9:
        matched_values = guessed_ons_mk9[hash_val]
        mk9_matches.append((hash_val, matched_values))

# mk10 = last_name + zip + year_of_birth
guessed_ons_mk10 = {
    hash_fields([ln, zipc, yob]): (ln, zipc, yob)
    for ln in top_last_names
    for zipc in top_zips
    for yob in top_yobs
}

# Find actual hits in df_ons["mk10"]
mk10_matches = []
for hash_val in df_ons["mk10"]:
    if hash_val in guessed_ons_mk10:
        matched_values = guessed_ons_mk10[hash_val]
        mk10_matches.append((hash_val, matched_values))

# mk11 = first + year_of_birth + zip[:3]
guessed_ons_mk11 = {
    hash_fields([fn, yob, str(zipc)[:3] if pd.notnull(zipc) else ""]): (fn, yob, zipc)
    for fn in top_first_names
    for yob in top_yobs
    for zipc in top_zips
}

# Find actual hits in df_ons["mk11"]
mk11_matches = []
for hash_val in df_ons["mk11"]:
    if hash_val in guessed_ons_mk11:
        matched_values = guessed_ons_mk11[hash_val]
        mk11_matches.append((hash_val, matched_values))

# mk12 = soundex(first_name) + last_name + dob
guessed_ons_mk12 = {
    hash_fields([soundex_simple(fn), ln, dob]): (fn, ln, dob)
    for fn in top_first_names
    for ln in top_last_names
    for dob in top_dobs
}

# Find actual hits in df_ons["mk12"]
mk12_matches = []
for hash_val in df_ons["mk12"]:
    if hash_val in guessed_ons_mk12:
        matched_values = guessed_ons_mk12[hash_val]
        mk12_matches.append((hash_val, matched_values))

# mk13 = last_name + year_of_birth + zip[:3]
guessed_ons_mk13 = {
    hash_fields([ln, yob, str(zipc)[:3] if pd.notnull(zipc) else ""]): (ln, yob, zipc)
    for ln in top_last_names
    for yob in top_yobs
    for zipc in top_zips
}

# Find actual hits in df_ons["mk13"]
mk13_matches = []
for hash_val in df_ons["mk13"]:
    if hash_val in guessed_ons_mk13:
        matched_values = guessed_ons_mk13[hash_val]
        mk13_matches.append((hash_val, matched_values))

# Compare to actual match keys
ons_mk1_hits = df_ons["mk1"].isin(guessed_ons_mk1).sum()
ons_mk2_hits = df_ons["mk2"].isin(guessed_ons_mk2).sum()
ons_mk3_hits = df_ons["mk3"].isin(guessed_ons_mk3).sum()
ons_mk4_hits = df_ons["mk4"].isin(guessed_ons_mk4).sum()
ons_mk5_hits = df_ons["mk5"].isin(guessed_ons_mk5).sum()
ons_mk6_hits = df_ons["mk6"].isin(guessed_ons_mk6).sum()
ons_mk7_hits = df_ons["mk7"].isin(guessed_ons_mk7).sum()
ons_mk8_hits = df_ons["mk8"].isin(guessed_ons_mk8).sum()
ons_mk9_hits = df_ons["mk9"].isin(guessed_ons_mk9).sum()
ons_mk10_hits = df_ons["mk10"].isin(guessed_ons_mk10).sum()
ons_mk11_hits = df_ons["mk11"].isin(guessed_ons_mk11).sum()
ons_mk12_hits = df_ons["mk12"].isin(guessed_ons_mk12).sum()
ons_mk13_hits = df_ons["mk13"].isin(guessed_ons_mk13).sum()

ons_attack_results = {
        "mk1_hits": ons_mk1_hits,
        "mk2_hits": ons_mk2_hits,
        "mk3_hits": ons_mk3_hits,
        "mk4_hits": ons_mk4_hits,
        "mk5_hits": ons_mk5_hits,
        "mk6_hits": ons_mk6_hits,
        "mk7_hits": ons_mk7_hits,
        "mk8_hits": ons_mk8_hits,
        "mk9_hits": ons_mk9_hits,
        "mk10_hits": ons_mk10_hits,
        "mk11_hits": ons_mk11_hits,
        "mk12_hits": ons_mk12_hits,
        "mk13_hits": ons_mk13_hits
    }

print(ons_attack_results)

# Open a file to write the output
output_file = "ons_attack_results.txt"
with open(output_file, "w", encoding="utf-8") as f:
    print("Used distribution: " + df_original_file, file=f)
    print("Used matchkeys: " + df_ons_file, file=f)

    # Write the ons_attack_results dictionary to the file
    print(ons_attack_results, file=f)

    # Print the matched combinations to the file
    if ons_mk1_hits != 0:
        print("Matched values for mk1 (first + last + dob):", file=f)
        for hash_val, values in mk1_matches:
            print(f"Hash: {hash_val}  ←  Values: {values}", file=f)

    if ons_mk2_hits != 0:
        print("Matched values for mk2 (first_initial + last + dob):", file=f)
        for hash_val, values in mk2_matches:
            print(f"Hash: {hash_val}  ←  Values: {values}", file=f)

    if ons_mk3_hits != 0:
        print("Matched values for mk3 (first + zip + dob):", file=f)
        for hash_val, values in mk3_matches:
            print(f"Hash: {hash_val}  ←  Values: {values}", file=f)

    if ons_mk4_hits != 0:
        print("Matched values for mk4 (soundex(last name) + dob):", file=f)
        for hash_val, values in mk4_matches:
            print(f"Hash: {hash_val}  ←  Values: {values}", file=f)   

    if ons_mk5_hits != 0:
        print("Matched values for mk5 (first[:3] + last + year_of_birth):", file=f)
        for hash_val, values in mk5_matches:
            print(f"Hash: {hash_val}  ←  Values: {values}", file=f)

    if ons_mk6_hits != 0:
        print("Matched values for mk6 (first + soundex(last name) + dob):", file=f)
        for hash_val, values in mk6_matches:
            print(f"Hash: {hash_val}  ←  Values: {values}", file=f)

    if ons_mk7_hits != 0:
        print("Matched values for mk7 (first_initial + soundex(last name) + dob):", file=f)
        for hash_val, values in mk7_matches:
            print(f"Hash: {hash_val}  ←  Values: {values}", file=f)

    if ons_mk8_hits != 0:
        print("Matched values for mk8 (first + last + dob[:7]):", file=f)
        for hash_val, values in mk8_matches:
            print(f"Hash: {hash_val}  ←  Values: {values}", file=f)

    if ons_mk9_hits != 0:
        print("Matched values for mk9 (first_initial + last_initial + year_of_birth):", file=f)
        for hash_val, values in mk9_matches:
            print(f"Hash: {hash_val}  ←  Values: {values}", file=f)

    if ons_mk10_hits != 0:
        print("Matched values for mk10 (last_name + zip + year_of_birth):", file=f)
        for hash_val, values in mk10_matches:
            print(f"Hash: {hash_val}  ←  Values: {values}", file=f)

    if ons_mk11_hits != 0:
        print("Matched values for mk11 (first + year_of_birth + zip[:3]):", file=f)
        for hash_val, values in mk11_matches:
            print(f"Hash: {hash_val}  ←  Values: {values}", file=f)

    if ons_mk12_hits != 0:
        print("Matched values for mk12 (soundex(first_name) + last_name + dob):", file=f)
        for hash_val, values in mk12_matches:
            print(f"Hash: {hash_val}  ←  Values: {values}", file=f)

    if ons_mk13_hits != 0:
        print("Matched values for mk13 (last_name + year_of_birth + zip[:3]):", file=f)
        for hash_val, values in mk13_matches:
            print(f"Hash: {hash_val}  ←  Values: {values}", file=f)

# Notify the user that the results have been saved
print(f"Results have been written to {output_file}")

""" # Print the matched combinations
if ons_mk1_hits != 0:
    print("Matched values for mk1 (first + last + dob):")
    for hash_val, values in mk1_matches:
        print(f"Hash: {hash_val}  ←  Values: {values}")

if ons_mk2_hits != 0:
    print("Matched values for mk2 (first_initial + last + dob):")
    for hash_val, values in mk2_matches:
        print(f"Hash: {hash_val}  ←  Values: {values}")

if ons_mk3_hits != 0:
    print("Matched values for mk3 (first + zip + dob):")
    for hash_val, values in mk3_matches:
        print(f"Hash: {hash_val}  ←  Values: {values}")

if ons_mk4_hits != 0:
    print("Matched values for mk4 (soundex(last name) + dob):")
    for hash_val, values in mk4_matches:
        print(f"Hash: {hash_val}  ←  Values: {values}")   

if ons_mk5_hits != 0:
    print("Matched values for mk5 (first[:3] + last + year_of_birth):")
    for hash_val, values in mk5_matches:
        print(f"Hash: {hash_val}  ←  Values: {values}")

if ons_mk6_hits != 0:
    print("Matched values for mk6 (first + soundex(last name) + dob):")
    for hash_val, values in mk6_matches:
        print(f"Hash: {hash_val}  ←  Values: {values}")

if ons_mk7_hits != 0:
    print("Matched values for mk7 (first_initial + soundex(last name) + dob):")
    for hash_val, values in mk7_matches:
        print(f"Hash: {hash_val}  ←  Values: {values}")

if ons_mk8_hits != 0:
    print("Matched values for mk8 (first + last + dob[:7]):")
    for hash_val, values in mk8_matches:
        print(f"Hash: {hash_val}  ←  Values: {values}")

if ons_mk9_hits != 0:
    print("Matched values for mk9 (first_initial + last_initial + year_of_birth):")
    for hash_val, values in mk9_matches:
        print(f"Hash: {hash_val}  ←  Values: {values}")

if ons_mk10_hits != 0:
    print("Matched values for mk10 (last_name + zip + year_of_birth):")
    for hash_val, values in mk10_matches:
        print(f"Hash: {hash_val}  ←  Values: {values}")

if ons_mk11_hits != 0:
    print("Matched values for mk11 (first + year_of_birth + zip[:3]):")
    for hash_val, values in mk11_matches:
        print(f"Hash: {hash_val}  ←  Values: {values}")

if ons_mk12_hits != 0:
    print("Matched values for mk12 (soundex(first_name) + last_name + dob):")
    for hash_val, values in mk12_matches:
        print(f"Hash: {hash_val}  ←  Values: {values}")

if ons_mk13_hits != 0:
    print("Matched values for mk13 (last_name + year_of_birth + zip[:3]):")
    for hash_val, values in mk13_matches:
        print(f"Hash: {hash_val}  ←  Values: {values}") """
