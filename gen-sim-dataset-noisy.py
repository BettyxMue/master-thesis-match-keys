import pandas as pd
import random
from faker import Faker
import re

# Reinitialize Faker after kernel reset
fake = Faker('de_DE')
Faker.seed(1234)
random.seed(1234)

# Helper to normalize strings
def normalize(s):
    return re.sub(r'\W+', '', s.lower().strip()) if s else ""

# Function to clean and extract first and last names robustly
def extract_clean_names_robust(profile_name):
    # Define a list of common German and academic prefixes/titles
    known_titles = {
        "dr", "prof", "bsc", "msc", "ba", "ma", "mba", "b.eng", "m.eng", "dipl", "dipl-ing", "diplom",
        "mag", "med", "herr", "frau", "ing", "univprof"
    }

    # Clean punctuation, lowercase, and split
    parts = re.sub(r'[^\wäöüÄÖÜß\- ]+', '', profile_name.lower()).split()

    # Filter out titles and honorifics
    name_parts = [part for part in parts if part not in known_titles]

    # Assign names based on what's left
    if len(name_parts) == 0:
        return "", ""
    elif len(name_parts) == 1:
        return name_parts[0].capitalize(), ""
    else:
        # Heuristic: first name is the first part, last name is the rest
        first_name = name_parts[0].capitalize()
        last_name = " ".join([p.capitalize() for p in name_parts[1:]])
        return first_name, last_name

# Function to generate a single record
def generate_german_record():
    gender = random.choice(['M', 'F'])
    profile = fake.simple_profile(sex='M' if gender == 'M' else 'F')

    # Extract clean first and last name
    first_name, last_name = extract_clean_names_robust(profile['name'])
    dob = profile['birthdate'].strftime('%Y-%m-%d')
    year_of_birth = profile['birthdate'].strftime('%Y')
    email = profile['mail']
    postcode = fake.postcode()
    phone = fake.phone_number()
    address = fake.street_address()
    city = fake.city()
    first_initial = first_name[0] if first_name else ""

    return {
        "first_name": first_name,
        "last_name": last_name,
        "dob": dob,
        "year_of_birth": year_of_birth,
        "gender": gender,
        "zip": postcode,
        "email": email,
        "phone": phone,
        "address": address,
        "city": city,
        "first_initial": first_initial
    }

# Function to introduce errors or missing data
def introduce_errors(record):
    def typo(s):
        if isinstance(s, str) and len(s) > 1:
            i = random.randint(0, len(s) - 2)
            return s[:i] + s[i + 1] + s[i] + s[i + 2:]
        return s

    # Reduce error and missing data probability
    for field in ["first_name", "last_name", "zip", "email", "address", "city", "phone"]:
        if random.random() < 0.05:
            record[field] = typo(record[field])
        elif random.random() < 0.05:
            record[field] = ""

    if random.random() < 0.05:
        record["gender"] = ""
    if random.random() < 0.05:
        record["phone"] = ""

    return record

# Generate and corrupt 500 records
noisy_records = [introduce_errors(generate_german_record()) for _ in range(500)]
df_noisy = pd.DataFrame(noisy_records)

# Save to CSV
noisy_csv_path = "german_healthcare_records_500_noisy.csv"
df_noisy.to_csv(noisy_csv_path, index=False)
