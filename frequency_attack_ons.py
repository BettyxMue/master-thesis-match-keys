import pandas as pd
import re
import hashlib
from scipy.stats import spearmanr
from jellyfish import soundex

# Load datasets
df_encoded = pd.read_csv("ons_13_matchkeys_output.csv")
df_plain = pd.read_csv("known-german_healthcare_records_500.csv")

# Helpers
def normalize(s):
    return re.sub(r'\W+', '', str(s).lower().strip()) if pd.notnull(s) else ""

def hash_fields(fields):
    combined = "".join(normalize(f) for f in fields if f)
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()

def generate_plaintext_combinations(df, fields):
    combos = df[fields].dropna().drop_duplicates()
    combos["plaintext_combo"] = combos[fields].astype(str).agg("|".join, axis=1)
    return combos["plaintext_combo"]

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

# Define candidate match-key combinations 
candidate_keys = {
    "mk_ons_1": ["first_name", "last_name", "dob"],
    "mk_ons_2": ["first_initial", "last_name", "dob"],
    "mk_ons_3": ["first_name", "zip", "dob"],
    "mk_ons_4": [soundex("last_name"), "dob"],
    "mk_ons_5": ["first_name"[:3], "last_name", "year_of_birth"],
    "mk_ons_6": ["first_name", soundex("last_name"), "dob"],
    "mk_ons_7": ["first_initial", soundex("last_name"), "dob"],
    "mk_ons_8": ["first_name", "last_name", "dob"[:7]],
    "mk_ons_9": ["first_initial", "last_name"[0], "year_of_birth"],
    "mk_ons_10": ["last_name", "zip", "year_of_birth"],
    "mk_ons_11": ["first_name", "year_of_birth", "zip"[:3]],
    "mk_ons_12": [soundex("first_name"), "last_name", "dob"],
    "mk_ons_13": ["last_name", "year_of_birth", "zip"[:3]]
}

# Generate plaintext hash frequencies
plaintext_hash_freqs = {}
for name, fields in candidate_keys.items():
    combos = generate_plaintext_combinations(df_plain, fields)
    hashed_combos = combos.apply(lambda x: hash_fields(x.split("|")))
    freqs = hashed_combos.value_counts()
    plaintext_hash_freqs[name] = freqs

# Compare to encoded matchkey frequencies
correlations = {}
for mk_col in df_encoded.columns:
    encoded_freq = df_encoded[mk_col].value_counts()
    top_encoded = encoded_freq[encoded_freq > 1]
    if top_encoded.empty:
        continue
    best_corr = 0
    best_key = None
    for key_name, freqs in plaintext_hash_freqs.items():
        common = top_encoded.index.intersection(freqs.index)
        if len(common) > 5:
            corr, _ = spearmanr(top_encoded[common], freqs[common])
            if corr > best_corr:
                best_corr = corr
                best_key = key_name
    correlations[mk_col] = (best_key, best_corr)

# Display results
correlation_results = pd.DataFrame.from_dict(correlations, orient="index", columns=["Best_Plaintext_Key", "Spearman_Correlation"])
print(correlation_results)