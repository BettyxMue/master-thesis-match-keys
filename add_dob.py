import pandas as pd
import random

# Function to generate a random day of birth while keeping the year
def generate_random_dob(year):
    if pd.notnull(year):  # Ensure the year is valid
        # Generate a random month (1 to 12)
        month = random.randint(1, 12)
        # Generate a random day based on the month and year
        if month in [1, 3, 5, 7, 8, 10, 12]:  # Months with 31 days
            day = random.randint(1, 31)
        elif month in [4, 6, 9, 11]:  # Months with 30 days
            day = random.randint(1, 30)
        else:  # February
            if (int(year) % 4 == 0 and int(year) % 100 != 0) or (int(year) % 400 == 0):  # Leap year
                day = random.randint(1, 29)
            else:
                day = random.randint(1, 28)
        # Return the generated date in YYYY-MM-DD format
        return f"{int(year):04d}-{month:02d}-{day:02d}"
    return None  # Return None if the year is invalid

# Input and output file paths
input_file = r"Raw_data/nc_voter_clean_new.csv"
output_file = r"Raw_data/nc_voter_clean_new_dob.csv"

# Load the dataset with explicit data types for 'zip' and 'phone'
df = pd.read_csv(input_file, dtype={"zip": str, "phone": str})

# Check and generate random 'dob' values if necessary
if "dob" not in df.columns or df["dob"].isnull().any():
    print("Generating random 'dob' values for missing entries...")
    # Create the 'dob' column if it doesn't exist
    if "dob" not in df.columns:
        df["dob"] = None
    # Apply the function to generate random 'dob' values for missing entries
    df["dob"] = df.apply(
        lambda row: generate_random_dob(row["year_of_birth"]) if pd.isnull(row["dob"]) else row["dob"],
        axis=1
    )
else:
    print("'dob' column already exists and has no missing values.")

# Save the updated dataset to a new file
df.to_csv(output_file, index=False)
print(f"Updated dataset saved to {output_file}")