import pandas as pd

# Load a sample of the NC voter dataset
file_path = "ncvoter_Statewide.txt"
df = pd.read_csv(file_path, delimiter="\t", dtype=str, encoding="ISO-8859-1")

# Select relevant columns
df_filtered = df[[
    "first_name",
    "middle_name",
    "last_name",
    "res_street_address",
    "res_city_desc",
    "zip_code",
    "full_phone_number",
    "gender_code",
    "birth_year"
]]

# Rename columns to match the structure of the simulated dataset
df_filtered = df_filtered.rename(columns={
    "first_name": "first_name",
    "middle_name": "middle_name",
    "last_name": "last_name",
    "res_street_address": "address",
    "res_city_desc": "city",
    "zip_code": "zip",
    "full_phone_number": "phone",
    "gender_code": "gender",
    "birth_year": "year_of_birth"
})

# Drop rows with missing names or birth year
df_filtered = df_filtered.dropna(subset=["first_name", "last_name", "year_of_birth"])

# Combine name parts to match previous format
df_filtered["first_name"] = df_filtered["first_name"].str.strip()
df_filtered["middle_name"] = df_filtered["middle_name"].fillna("").str.strip()
df_filtered["last_name"] = df_filtered["last_name"].str.strip()

# Replace 'REMOVED' or similar terms with empty string in address and related fields
df_filtered["address"] = df_filtered["address"].replace(r"(?i)^removed$", "", regex=True)
df_filtered["city"] = df_filtered["city"].replace(r"(?i)^removed$", "", regex=True)

# Remove '#' characters from last names (or any other field)
df_filtered["last_name"] = df_filtered["last_name"].str.replace("#", "", regex=False)

# Optional: Strip whitespace and standardize formatting
df_filtered["last_name"] = df_filtered["last_name"].str.strip()
df_filtered["address"] = df_filtered["address"].str.strip()
df_filtered["city"] = df_filtered["city"].str.strip()

# Ensure phone and zip are strings and clean whitespace
df_filtered["phone"] = df_filtered["phone"].fillna("").astype(str).str.strip()
df_filtered["zip"] = df_filtered["zip"].fillna("").astype(str).str.strip()
df_filtered["gender"] = df_filtered["gender"].fillna("").str.upper().str.strip()

# Save the cleaned version
output_path = "nc_voter_clean.csv"
df_filtered.to_csv(output_path, index=False)
