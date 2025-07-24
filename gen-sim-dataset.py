from faker import Faker
import pandas as pd
import random

# Initialize Faker
fake = Faker('de_DE')
Faker.seed(1234)
random.seed(1234)

# Function to generate a German-style healthcare record
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

# Generate 500 records
records = [generate_german_record() for _ in range(500)]
df = pd.DataFrame(records)

# Save to CSV
csv_path = "german_healthcare_records_500.csv"
df.to_csv(csv_path, index=False)