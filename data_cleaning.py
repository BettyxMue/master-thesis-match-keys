import pandas as pd

# Load a sample of the NC voter dataset
file_path = "ohio_voter.txt"
# df = pd.read_csv(file_path, delimiter="\t", dtype=str, encoding="ISO-8859-1")
df = pd.read_csv(file_path, delimiter=",", quotechar='"', dtype=str, encoding="utf-8")

print(df.columns)

# ___________North Carolina___________
# Select relevant columns
""" df_filtered = df[[
    "first_name",
    "middle_name",
    "last_name",
    "res_street_address",
    "res_city_desc",
    "zip_code",
    "full_phone_number",
    "gender_code",
    "birth_year"
]] """

# Rename columns to match the structure of the simulated dataset
""" df_filtered = df_filtered.rename(columns={
    "first_name": "first_name",
    "middle_name": "middle_name",
    "last_name": "last_name",
    "res_street_address": "address",
    "res_city_desc": "city",
    "zip_code": "zip",
    "full_phone_number": "phone",
    "gender_code": "gender",
    "birth_year": "year_of_birth"
}) """

#____________Ohio_____________
# Select relevant columns
df_filtered = df[[
    "FIRST_NAME",
    "MIDDLE_NAME",
    "LAST_NAME",
    "DATE_OF_BIRTH",
    "RESIDENTIAL_ADDRESS1",
    "RESIDENTIAL_CITY",
    "RESIDENTIAL_ZIP",
]]

# Rename columns to match the structure of the simulated dataset
df_filtered = df_filtered.rename(columns={
    "FIRST_NAME": "first_name",
    "MIDDLE_NAME": "middle_name",
    "LAST_NAME": "last_name",
    "DATE_OF_BIRTH": "dob",
    "RESIDENTIAL_ADDRESS1": "address",
    "RESIDENTIAL_CITY": "city",
    "RESIDENTIAL_ZIP": "zip"
})

# Drop rows with missing names or birth year
# df_filtered = df_filtered.dropna(subset=["first_name", "last_name", "year_of_birth"])

# Combine name parts to match previous format
df_filtered["first_name"] = df_filtered["first_name"].str.strip().str.lower()
df_filtered["middle_name"] = df_filtered["middle_name"].fillna("").str.strip().str.lower()
df_filtered["last_name"] = df_filtered["last_name"].str.strip().str.lower()

# Replace 'REMOVED' or similar terms with empty string in address and related fields
df_filtered["address"] = df_filtered["address"].replace(r"(?i)^removed$", "", regex=True).str.lower()
df_filtered["city"] = df_filtered["city"].replace(r"(?i)^removed$", "", regex=True).str.lower()

# Remove '#' characters from last names (or any other field)
df_filtered["last_name"] = df_filtered["last_name"].str.replace("#", "", regex=False)

# Optional: Strip whitespace and standardize formatting
df_filtered["last_name"] = df_filtered["last_name"].str.strip().str.lower()
df_filtered["address"] = df_filtered["address"].str.strip().str.lower()
df_filtered["city"] = df_filtered["city"].str.strip().str.lower()

# Ensure phone and zip are strings and clean whitespace
# df_filtered["phone"] = df_filtered["phone"].fillna("").astype(str).str.strip().str.lower()
df_filtered["zip"] = df_filtered["zip"].fillna("").astype(str).str.strip().str.lower()
# df_filtered["gender"] = df_filtered["gender"].fillna("").str.lower().str.strip()

# Add a column with the first initial of the first name (still uppercase for initials)
df_filtered["first_initial"] = df_filtered["first_name"].str[0].str.upper()

# Extract the birth year from the date of birth
df_filtered["year_of_birth"] = df_filtered["dob"].str[:4]

# Save the cleaned version
output_path = "ohio_voter_clean.csv"
df_filtered.to_csv(output_path, index=False)
