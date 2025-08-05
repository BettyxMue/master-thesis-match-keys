import pandas as pd
import re
import hashlib
from scipy.stats import spearmanr
import matplotlib.pyplot as plt
from scipy.spatial.distance import jensenshannon
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Reload required CSV files
df_encoded = pd.read_csv(r"Gen_match_keys/nc_voter_dob_matchkeys_randall.csv")
df_plain = pd.read_csv(r"Raw_data/ohio_voter_clean_new.csv")

# Helper functions
def normalize(s):
    return re.sub(r'\W+', '', str(s).lower().strip()) if pd.notnull(s) else ""

def hash_fields(fields):
    combined = "".join(normalize(f) for f in fields if f)
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()

def generate_plaintext_combinations(df, fields):
    combos = df[fields].dropna()
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

# Step 3: Compare with encoded matchkey distributions using Jensen-Shannon and Cosine
results = []
for mk_col in df_encoded.columns:
    encoded_freq = df_encoded[mk_col].value_counts()
    top_encoded = encoded_freq[encoded_freq >= 1]
    if top_encoded.empty:
        continue
    for key_name, freqs in plaintext_hash_freqs.items():
        common = top_encoded.index.intersection(freqs.index)
        # Build the union of keys instead of just the intersection
        union_keys = top_encoded.index.union(freqs.index)

        # Align both distributions to the union set
        encoded_vals = top_encoded.reindex(union_keys, fill_value=0).values
        plain_vals = freqs.reindex(union_keys, fill_value=0).values

        # Optional: Apply log-scaling to dampen dominant values
        encoded_vals = np.log1p(encoded_vals)  # log(1 + x) is safe for zeros
        plain_vals = np.log1p(plain_vals)

        # Normalize to create probability distributions
        encoded_probs = encoded_vals / encoded_vals.sum()
        plain_probs = plain_vals / plain_vals.sum()

        # Calculate similarity scores
        js = 1 - jensenshannon(encoded_probs, plain_probs)
        cos = cosine_similarity([encoded_vals], [plain_vals])[0][0]

        results.append((mk_col, key_name, js, cos))

# Create result DataFrame
result_df = pd.DataFrame(results, columns=["Matchkey", "Plaintext_Key", "Jensen-Shannon", "Cosine"])

# Bar chart of correlation values with spearman
if correlation_results.empty == True:
    print("No correlations with Spearman found.")
else:
    plt.figure(figsize=(10, 6))
    plt.barh(correlation_results.index, correlation_results["Spearman_Correlation"], color="skyblue")
    plt.xlabel("Spearman Correlation")
    plt.title("Correlation between Encoded Matchkeys and Plaintext Key Frequencies (Randall)")
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.grid(True)
    plt.show()

# Sort and select top 10 for plotting
top_js = result_df.sort_values(by="Jensen-Shannon", ascending=False)
top_cosine = result_df.sort_values(by="Cosine", ascending=False)

# Plot Jensen-Shannon Similarity
if top_js.empty == True:
    print("No correlations with Jensen-Shannon found.")
else:
    plt.figure(figsize=(12, 6))
    y_pos_js = np.arange(len(top_js))
    labels_js = [f"{mk} ({pt})" for mk, pt in zip(top_js["Matchkey"], top_js["Plaintext_Key"])]

    plt.barh(y_pos_js, top_js["Jensen-Shannon"], color="lightcoral")
    plt.yticks(y_pos_js, labels_js)
    plt.xlabel("Jensen-Shannon Similarity")
    plt.title("Jensen-Shannon Similarities between Encoded and Plaintext Keys")
    plt.gca().invert_yaxis()
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

# Plot Cosine Similarity
if top_cosine.empty == True:
    print("No correlations with Cosine found.")
else:
    plt.figure(figsize=(12, 6))
    y_pos_cos = np.arange(len(top_cosine))
    labels_cos = [f"{mk} ({pt})" for mk, pt in zip(top_cosine["Matchkey"], top_cosine["Plaintext_Key"])]

    plt.barh(y_pos_cos, top_cosine["Cosine"], color="skyblue")
    plt.yticks(y_pos_cos, labels_cos)
    plt.xlabel("Cosine Similarity")
    plt.title("Cosine Similarities between Encoded and Plaintext Keys")
    plt.gca().invert_yaxis()
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

print("\nTop Correlations per Metric:")
print("Spearman:")
print(correlation_results.head(5))
print("\nJensen-Shannon:")
print(top_js.head(5))
print("\nCosine:")
print(top_cosine.head(5))