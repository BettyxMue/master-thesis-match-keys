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

# Function to generate a single record
def generate_german_record():
    gender = random.choice(['M', 'F'])
    profile = fake.simple_profile(sex='M' if gender == 'M' else 'F')
    
    name_parts = profile['name'].split()
    first_name = name_parts[0]
    last_name = name_parts[-1]
    dob = profile['birthdate'].strftime('%Y-%m-%d')
    year_of_birth = profile['birthdate'].strftime('%Y')
    email = profile['mail']
    postcode = fake.postcode()
    phone = fake.phone_number()
    address = fake.street_address()
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
        "first_initial": first_initial
    }

# Function to introduce errors or missing data
def introduce_errors(record):
    def typo(s):
        if len(s) > 1:
            i = random.randint(0, len(s)-2)
            return s[:i] + s[i+1] + s[i] + s[i+2:]
        return s

    for field in ["first_name", "last_name", "zip", "email", "address"]:
        if random.random() < 0.1:
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
