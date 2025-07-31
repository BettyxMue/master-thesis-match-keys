import pandas as pd
import re
import hashlib
from scipy.stats import spearmanr

# Load datasets
df_encoded = pd.read_csv("ons_13_matchkeys_output.csv")
df_plain = pd.read_csv("known-german_healthcare_records_500.csv")

# Create 'dob' if missing
if "dob" not in df_plain.columns and "year_of_birth" in df_plain.columns:
    df_plain["dob"] = df_plain["year_of_birth"].apply(lambda y: f"{y}-01-01" if pd.notnull(y) else "")

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

# Define candidate match-key combinations (adjust as needed)
candidate_keys = {
    "first_last_dob": ["first_name", "last_name", "dob"],
    "initial_last_dob": ["first_name", "last_name", "dob"],
    "first_zip_dob": ["first_name", "zip", "dob"],
    "last_dob": ["last_name", "dob"],
    "first3_last_yob": ["first_name", "last_name", "year_of_birth"]
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