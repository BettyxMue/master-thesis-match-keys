from matplotlib import pyplot as plt
import pandas as pd
import re
import hashlib
from scipy.stats import spearmanr
from jellyfish import soundex
from scipy.spatial.distance import jensenshannon
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Load datasets
df_encoded = pd.read_csv(r"Gen_match_keys/ohio_voter_matchkeys_randall.csv")
df_plain = pd.read_csv(r"Raw_data/nc_voter_clean_new_dob.csv")

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

from jellyfish import soundex

def transform_fields(row, fields, key_name):
    transformed = []
    for f in fields:
        val = row.get(f, "")
        if pd.isnull(val):
            val = ""

        # Apply special transformations based on match key logic
        if key_name == "mk_ons_4" and f == "last_name":
            val = soundex(str(val))

        elif key_name == "mk_ons_5" and f == "first_name":
            val = str(val)[:3]

        elif key_name == "mk_ons_6" and f == "last_name":
            val = soundex(str(val))

        elif key_name == "mk_ons_7" and f == "last_name":
            val = soundex(str(val))

        elif key_name == "mk_ons_8" and f == "dob":
            val = str(val)[:7]  # 'YYYY-MM'

        elif key_name == "mk_ons_9" and f == "last_name":
            val = str(val)[0] if val else ""

        elif key_name == "mk_ons_11" and f == "zip":
            val = str(val)[:3]

        elif key_name == "mk_ons_12" and f == "first_name":
            val = soundex(str(val))

        elif key_name == "mk_ons_13" and f == "zip":
            val = str(val)[:3]

        transformed.append(val)

    return transformed

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
    "mk_ons_4": ["last_name", "dob"],  # soundex will be applied later
    "mk_ons_5": ["first_name", "last_name", "year_of_birth"],  # slicing handled later
    "mk_ons_6": ["first_name", "last_name", "dob"],  # apply soundex to last
    "mk_ons_7": ["first_initial", "last_name", "dob"],  # soundex on last
    "mk_ons_8": ["first_name", "last_name", "dob"],  # truncate dob later
    "mk_ons_9": ["first_initial", "last_name", "year_of_birth"],  # get first char of last
    "mk_ons_10": ["last_name", "zip", "year_of_birth"],
    "mk_ons_11": ["first_name", "year_of_birth", "zip"],
    "mk_ons_12": ["first_name", "last_name", "dob"],  # soundex on first
    "mk_ons_13": ["last_name", "year_of_birth", "zip"]
}

# Generate plaintext hash frequencies
plaintext_hash_freqs = {}
for name, fields in candidate_keys.items():
    if not all(f in df_plain.columns for f in fields):
        print(f"Skipping {name}, missing fields.")
        continue

    # Apply transformation row-wise
    hashed_combos = (
        df_plain.dropna(subset=fields)
        .drop_duplicates(subset=fields)
        .apply(lambda row: hash_fields(transform_fields(row, fields, name)), axis=1)
    )

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

# Step 3: Compare with encoded matchkey distributions using Jensen-Shannon and Cosine
results = []
for mk_col in df_encoded.columns:
    encoded_freq = df_encoded[mk_col].value_counts()
    top_encoded = encoded_freq[encoded_freq >= 1]
    if top_encoded.empty:
        continue
    for key_name, freqs in plaintext_hash_freqs.items():
        common = top_encoded.index.intersection(freqs.index)
        if len(common) >= 3:
            encoded_vals = top_encoded[common].values
            plain_vals = freqs[common].values

            # Normalize
            encoded_probs = encoded_vals / np.sum(encoded_vals)
            plain_probs = plain_vals / np.sum(plain_vals)

            js = 1 - jensenshannon(encoded_probs, plain_probs)
            cos = cosine_similarity([encoded_vals], [plain_vals])[0][0]

            results.append((mk_col, key_name, js, cos))

# Create result DataFrame
result_df = pd.DataFrame(results, columns=["Matchkey", "Plaintext_Key", "Jensen-Shannon", "Cosine"])

# Sort and select top 10 for plotting
top_js = result_df.sort_values(by="Jensen-Shannon", ascending=False)
top_cosine = result_df.sort_values(by="Cosine", ascending=False)

# Plot Jensen-Shannon Similarity
plt.figure(figsize=(12, 6))
plt.barplot(data=top_js, x="Jensen-Shannon", y="Matchkey", hue="Plaintext_Key", dodge=False)
plt.title("Top 10 Jensen-Shannon Similarities between Encoded and Plaintext Keys")
plt.xlabel("Jensen-Shannon Similarity")
plt.ylabel("Match Key")
plt.legend(title="Plaintext Key", bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()

# Plot Cosine Similarity
plt.figure(figsize=(12, 6))
plt.barplot(data=top_cosine, x="Cosine", y="Matchkey", hue="Plaintext_Key", dodge=False)
plt.title("Top 10 Cosine Similarities between Encoded and Plaintext Keys")
plt.xlabel("Cosine Similarity")
plt.ylabel("Match Key")
plt.legend(title="Plaintext Key", bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()

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
