import pandas as pd
import re
import hashlib
from scipy.stats import spearmanr
import matplotlib.pyplot as plt

# Reload required CSV files
df_encoded = pd.read_csv(r"Gen_match_keys/ohio_voter_matchkeys_randall.csv")
df_plain = pd.read_csv(r"Raw_data/nc_voter_clean_new_dob.csv")

# Helper functions
def normalize(s):
    return re.sub(r'\W+', '', str(s).lower().strip()) if pd.notnull(s) else ""

def hash_fields(fields):
    combined = "".join(normalize(f) for f in fields if f)
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()

def generate_plaintext_combinations(df, fields):
    combos = df[fields].dropna().drop_duplicates()
    combos["plaintext_combo"] = combos[fields].astype(str).agg("|".join, axis=1)
    return combos["plaintext_combo"]

# Define candidate match-key attribute sets based on improved Randall algorithm
candidate_keys = {
    "mk_randall_1": ["first_name", "last_name", "dob"],
    "mk_randall_2": ["first_name", "zip", "year_of_birth"],
    "mk_randall_3": ["last_name", "dob", "gender"],
    "mk_randall_4": ["first_name", "gender", "zip"],
    "mk_randall_5": ["first_name", "last_name", "email"],
    "mk_randall_6": ["last_name", "year_of_birth", "zip"],
    "mk_randall_7": ["first_initial", "last_name", "dob"],
    "mk_randall_8": ["first_name", "address", "zip"],
    "mk_randall_9": ["first_name", "dob", "email"],
    "mk_randall_10": ["last_name", "gender", "email"]
}

# Step 1: Generate hashed frequencies of plaintext match-key combinations
plaintext_hash_freqs = {}
for name, fields in candidate_keys.items():
    if all(f in df_plain.columns for f in fields):
        combos = generate_plaintext_combinations(df_plain, fields)
        hashed_combos = combos.str.split("|").apply(hash_fields)
        freqs = hashed_combos.value_counts()
        plaintext_hash_freqs[name] = freqs

# Step 2: Compare with encoded matchkey distributions using Spearman correlation
correlations = {}
for mk_col in df_encoded.columns:
    encoded_freq = df_encoded[mk_col].value_counts()
    top_encoded = encoded_freq[encoded_freq >= 1] #or skip filter entirely
    if top_encoded.empty:
        continue
    best_corr = 0
    best_key = None
    for key_name, freqs in plaintext_hash_freqs.items():
        common = top_encoded.index.intersection(freqs.index)
        if len(common) >= 3:
            encoded_vals = top_encoded[common].values
            plain_vals = freqs[common].values
            if len(set(encoded_vals)) > 1 and len(set(plain_vals)) > 1:
                corr, _ = spearmanr(encoded_vals, plain_vals)
            else:
                corr = 0  # Or you can use `float('nan')` if you want to exclude it
            if corr > best_corr:
                best_corr = corr
                best_key = key_name
    # Only store meaningful correlations
    if best_key and best_corr > 0:
        correlations[mk_col] = (best_key, best_corr)

# Prepare and visualize results
correlation_results = pd.DataFrame.from_dict(correlations, orient="index", columns=["Best_Plaintext_Key", "Spearman_Correlation"])
correlation_results.sort_values(by="Spearman_Correlation", ascending=False, inplace=True)

# Bar chart of correlation values
if correlation_results.empty == True:
    print("No correlations found.")
else:
    plt.figure(figsize=(10, 6))
    plt.barh(correlation_results.index, correlation_results["Spearman_Correlation"], color="skyblue")
    plt.xlabel("Spearman Correlation")
    plt.title("Correlation between Encoded Matchkeys and Plaintext Key Frequencies (Randall)")
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.grid(True)
    plt.show()
