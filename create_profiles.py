import re
from gender_guesser.detector import Detector

def generate_profile_key(*args):
    return "_".join(str(arg).lower() for arg in args if arg is not None)

def normalize_field(value):
    return re.sub(r'\W+', '', str(value).strip().lower()) if value else None

def normalize_zip(zip_code):
    return re.sub(r'\D', '', str(zip_code)) if zip_code else None

# Function to merge two profiles (selecting a representative hash)
def merge_profiles(existing_profile, new_data):
    # Keep the first hash encountered as the representative hash
    if "hash" not in existing_profile:
        existing_profile["hash"] = new_data["hash"]

    # Update day of birth if missing or if new_data provides a more specific value
    if existing_profile.get("date_of_birth") == None and new_data.get("date_of_birth"):
        existing_profile["date_of_birth"] = new_data["date_of_birth"]
    # Handle conflicting day of birth (optional: log conflicts)
    elif existing_profile.get("date_of_birth") and new_data.get("date_of_birth"):
        if existing_profile["date_of_birth"] != new_data["date_of_birth"]:
            print(f"Conflict in day of birth for {existing_profile.get('first_name', 'Unknown')} {existing_profile.get('last_name', 'Unknown')}: "
                  f"{existing_profile['date_of_birth']} vs {new_data['date_of_birth']}")
            
    # Merge gender
    if existing_profile.get("gender") is None and new_data.get("gender"):
        existing_profile["gender"] = new_data["gender"]
    elif existing_profile.get("gender") and new_data.get("gender"):
        if existing_profile["gender"] != new_data["gender"]:
            print(f"Conflict in gender for {existing_profile.get('first_name', 'Unknown')} {existing_profile.get('last_name', 'Unknown')}: "
                  f"{existing_profile['gender']} vs {new_data['gender']}")
    # Deduce gender using the first name if not already set, using a library
    if existing_profile.get("gender") is None and existing_profile.get("first_name"):
        detector = Detector()
        first_name = existing_profile["first_name"].capitalize()
        guessed_gender = detector.get_gender(first_name)
        if guessed_gender in ["male", "mostly_male"]:
            existing_profile["gender"] = "male"
        elif guessed_gender in ["female", "mostly_female"]:
            existing_profile["gender"] = "female"
    return existing_profile

# Main function to process input and output profiles
def consolidate_profiles(input_file, output_file):
    # Dictionary to store unified profiles
    profiles = {}

    # Read and parse the input file
    with open(input_file, "r", encoding="utf-8") as f:  # Specify UTF-8 encoding
        current_match_key = None
        for line in f:
            line = line.strip()
            if not line:
                continue  # Skip empty lines

            # Check if the line indicates a new match key
            if line.startswith("Matches for"):
                current_match_key = line.split("(")[0].split()[-1]
                continue

            # Parse hash and plain text values
            if line.startswith("Hash:"):
                parts = line.split("←")
                hash_val = parts[0].split("Hash:")[1].strip()
                plain_values = eval(parts[1].split("Values:")[1].strip())  # Convert string tuple to actual tuple

                # Handle different match key formats
                # ---------- Randall Match Keys Handling ----------
                # Format: mk_randall_1 -> first_name, last_name, dob
                if current_match_key == "mk_randall_1" and len(plain_values) == 3:
                    first_name, last_name, dob = plain_values
                    year_of_birth = dob.split('-')[0] if '-' in dob else None
                    key = generate_profile_key(first_name, last_name, year_of_birth, dob)
                    new_data = {
                        "first_name": normalize_field(first_name),
                        "last_name": normalize_field(last_name),
                        "dob": dob,
                        "year_of_birth": year_of_birth,
                        "hash": hash_val,
                    }

                # Format: mk_randall_2 -> first_name, zip_code, year_of_birth
                elif current_match_key == "mk_randall_2" and len(plain_values) == 3:
                    first_name, zip_code, year_of_birth = plain_values
                    key = generate_profile_key(first_name, year_of_birth)
                    new_data = {
                        "first_name": normalize_field(first_name),
                        "zip_code": normalize_zip(zip_code),
                        "year_of_birth": year_of_birth,
                        "hash": hash_val,
                    }

                # Format: mk_randall_3 -> last_name, dob, gender
                elif current_match_key == "mk_randall_3" and len(plain_values) == 3:
                    last_name, dob, gender = plain_values
                    year_of_birth = dob.split('-')[0] if '-' in dob else None
                    key = generate_profile_key(last_name, year_of_birth, dob)
                    new_data = {
                        "last_name": normalize_field(last_name),
                        "dob": dob,
                        "gender": normalize_field(gender),
                        "year_of_birth": year_of_birth,
                        "hash": hash_val,
                    }

                # Format: mk_randall_4 -> first_name, gender, zip_code
                elif current_match_key == "mk_randall_4" and len(plain_values) == 3:
                    first_name, gender, zip_code = plain_values
                    key = generate_profile_key(first_name, zip_code)
                    new_data = {
                        "first_name": normalize_field(first_name),
                        "gender": normalize_field(gender),
                        "zip_code": normalize_zip(zip_code),
                        "hash": hash_val,
                    }

                # Format: mk_randall_5 -> first_name, last_name, email
                elif current_match_key == "mk_randall_5" and len(plain_values) == 3:
                    first_name, last_name, email = plain_values
                    key = generate_profile_key(first_name, last_name)
                    new_data = {
                        "first_name": normalize_field(first_name),
                        "last_name": normalize_field(last_name),
                        "email": normalize_field(email),
                        "hash": hash_val,
                    }

                # Format: mk_randall_6 -> last_name, year_of_birth, zip_code
                elif current_match_key == "mk_randall_6" and len(plain_values) == 3:
                    last_name, year_of_birth, zip_code = plain_values
                    key = generate_profile_key(last_name, year_of_birth)
                    new_data = {
                        "last_name": normalize_field(last_name),
                        "year_of_birth": year_of_birth,
                        "zip_code": normalize_zip(zip_code),
                        "hash": hash_val,
                    }

                # Format: mk_randall_7 -> first_initial, last_name, dob
                elif current_match_key == "mk_randall_7" and len(plain_values) == 3:
                    first_initial, last_name, dob = plain_values
                    year_of_birth = dob.split('-')[0] if '-' in dob else None
                    key = generate_profile_key(first_initial, last_name, year_of_birth, dob)
                    new_data = {
                        "first_initial": normalize_field(first_initial),
                        "last_name": normalize_field(last_name),
                        "dob": dob,
                        "year_of_birth": year_of_birth,
                        "hash": hash_val,
                    }

                # Format: mk_randall_8 -> first_name, address, zip_code
                elif current_match_key == "mk_randall_8" and len(plain_values) == 3:
                    first_name, address, zip_code = plain_values
                    key = generate_profile_key(first_name, zip_code)
                    new_data = {
                        "first_name": normalize_field(first_name),
                        "address": normalize_field(address),
                        "zip_code": normalize_zip(zip_code),
                        "hash": hash_val,
                    }

                # Format: mk_randall_9 -> first_name, dob, email
                elif current_match_key == "mk_randall_9" and len(plain_values) == 3:
                    first_name, dob, email = plain_values
                    year_of_birth = dob.split('-')[0] if '-' in dob else None
                    key = generate_profile_key(first_name, year_of_birth, dob)
                    new_data = {
                        "first_name": normalize_field(first_name),
                        "dob": dob,
                        "email": normalize_field(email),
                        "year_of_birth": year_of_birth,
                        "hash": hash_val,
                    }

                # Format: mk_randall_10 -> last_name, gender, email
                elif current_match_key == "mk_randall_10" and len(plain_values) == 3:
                    last_name, gender, email = plain_values
                    key = generate_profile_key(last_name, gender)
                    new_data = {
                        "last_name": normalize_field(last_name),
                        "gender": normalize_field(gender),
                        "email": normalize_field(email),
                        "hash": hash_val,
                    }

                # ---------- ONS Match Keys Handling ----------
                # mk_ons_1: first_name, last_name, dob
                elif current_match_key == "mk_ons_1" and len(plain_values) == 3:
                    first_name, last_name, dob = plain_values
                    year_of_birth = dob.split("-")[0]
                    key = generate_profile_key(first_name, last_name, year_of_birth, dob)
                    new_data = {
                        "first_name": normalize_field(first_name),
                        "last_name": normalize_field(last_name),
                        "dob": dob,
                        "year_of_birth": year_of_birth,
                        "hash": hash_val,
                    }

                # mk_ons_2: last_name, dob, gender
                elif current_match_key == "mk_ons_2" and len(plain_values) == 3:
                    last_name, dob, gender = plain_values
                    year_of_birth = dob.split("-")[0]
                    key = generate_profile_key(last_name, year_of_birth, dob)
                    new_data = {
                        "last_name": normalize_field(last_name),
                        "dob": dob,
                        "gender": normalize_field(gender),
                        "year_of_birth": year_of_birth,
                        "hash": hash_val,
                    }

                # mk_ons_3: first_name, dob, gender
                elif current_match_key == "mk_ons_3" and len(plain_values) == 3:
                    first_name, dob, gender = plain_values
                    year_of_birth = dob.split("-")[0]
                    key = generate_profile_key(first_name, year_of_birth, dob)
                    new_data = {
                        "first_name": normalize_field(first_name),
                        "dob": dob,
                        "gender": normalize_field(gender),
                        "year_of_birth": year_of_birth,
                        "hash": hash_val,
                    }

                # mk_ons_4: first_name, last_name, gender
                elif current_match_key == "mk_ons_4" and len(plain_values) == 3:
                    first_name, last_name, gender = plain_values
                    key = generate_profile_key(first_name, last_name, gender)
                    new_data = {
                        "first_name": normalize_field(first_name),
                        "last_name": normalize_field(last_name),
                        "gender": normalize_field(gender),
                        "hash": hash_val,
                    }

                # mk_ons_5: first_name, last_name, postcode
                elif current_match_key == "mk_ons_5" and len(plain_values) == 3:
                    first_name, last_name, postcode = plain_values
                    key = generate_profile_key(first_name, last_name, postcode)
                    new_data = {
                        "first_name": normalize_field(first_name),
                        "last_name": normalize_field(last_name),
                        "zip_code": normalize_zip(postcode),
                        "hash": hash_val,
                    }

                # mk_ons_6: last_name, dob, postcode
                elif current_match_key == "mk_ons_6" and len(plain_values) == 3:
                    last_name, dob, postcode = plain_values
                    year_of_birth = dob.split("-")[0]
                    key = generate_profile_key(last_name, year_of_birth, dob)
                    new_data = {
                        "last_name": normalize_field(last_name),
                        "dob": dob,
                        "year_of_birth": year_of_birth,
                        "zip_code": normalize_zip(postcode),
                        "hash": hash_val,
                    }

                # mk_ons_7: first_name, dob, postcode
                elif current_match_key == "mk_ons_7" and len(plain_values) == 3:
                    first_name, dob, postcode = plain_values
                    year_of_birth = dob.split("-")[0]
                    key = generate_profile_key(first_name, year_of_birth, dob)
                    new_data = {
                        "first_name": normalize_field(first_name),
                        "dob": dob,
                        "year_of_birth": year_of_birth,
                        "zip_code": normalize_zip(postcode),
                        "hash": hash_val,
                    }

                # mk_ons_8: last_name, gender, postcode
                elif current_match_key == "mk_ons_8" and len(plain_values) == 3:
                    last_name, gender, postcode = plain_values
                    key = generate_profile_key(last_name, gender, postcode)
                    new_data = {
                        "last_name": normalize_field(last_name),
                        "gender": normalize_field(gender),
                        "zip_code": normalize_zip(postcode),
                        "hash": hash_val,
                    }

                # mk_ons_9: first_name, gender, postcode
                elif current_match_key == "mk_ons_9" and len(plain_values) == 3:
                    first_name, gender, postcode = plain_values
                    key = generate_profile_key(first_name, gender, postcode)
                    new_data = {
                        "first_name": normalize_field(first_name),
                        "gender": normalize_field(gender),
                        "zip_code": normalize_zip(postcode),
                        "hash": hash_val,
                    }

                # mk_ons_10: first_initial, dob, postcode
                elif current_match_key == "mk_ons_10" and len(plain_values) == 3:
                    first_initial, dob, postcode = plain_values
                    year_of_birth = dob.split("-")[0]
                    key = generate_profile_key(first_initial, year_of_birth, dob)
                    new_data = {
                        "first_initial": normalize_field(first_initial),
                        "dob": dob,
                        "year_of_birth": year_of_birth,
                        "zip_code": normalize_zip(postcode),
                        "hash": hash_val,
                    }

                # mk_ons_11: last_name, postcode
                elif current_match_key == "mk_ons_11" and len(plain_values) == 2:
                    last_name, postcode = plain_values
                    key = generate_profile_key(last_name, postcode)
                    new_data = {
                        "last_name": normalize_field(last_name),
                        "zip_code": normalize_zip(postcode),
                        "hash": hash_val,
                    }

                # mk_ons_12: first_name, postcode
                elif current_match_key == "mk_ons_12" and len(plain_values) == 2:
                    first_name, postcode = plain_values
                    key = generate_profile_key(first_name, postcode)
                    new_data = {
                        "first_name": normalize_field(first_name),
                        "zip_code": normalize_zip(postcode),
                        "hash": hash_val,
                    }

                # mk_ons_13: postcode, gender
                elif current_match_key == "mk_ons_13" and len(plain_values) == 2:
                    postcode, gender = plain_values
                    key = generate_profile_key(postcode, gender)
                    new_data = {
                        "zip_code": normalize_zip(postcode),
                        "gender": normalize_field(gender),
                        "hash": hash_val,
                    }

                else:
                    print(f"Unknown or unmatched format for {current_match_key}: {plain_values}")
                    continue

                # Merge into profiles or create a new profile
                if key in profiles:
                    profiles[key] = merge_profiles(profiles[key], new_data)
                else:
                    # Create a new profile if no match is found
                    profiles[key] = new_data

    # Write the unified profiles to the output file
    with open(output_file, "w", encoding="utf-8") as f:  # Specify UTF-8 encoding for output
        # Write the total number of distinct profiles
        f.write(f"Total Distinct Profiles: {len(profiles)}\n\n")
        
        for key, profile in profiles.items():
            f.write(f"Profile Key: {key}\n")
            f.write(f"  First Name: {profile.get('first_name', 'None')}\n")  # Use .get() to handle missing keys
            f.write(f"  Last Name: {profile.get('last_name', 'None')}\n")    # Use .get() to handle missing keys
            f.write(f"  Year of Birth: {profile.get('year_of_birth', 'None')}\n")
            f.write(f"  Date of Birth: {profile.get('date_of_birth', 'None')}\n")
            f.write(f"  Gender: {profile.get('gender', 'None')}\n")
            f.write(f"  Email: {profile.get('email', 'None')}\n")
            f.write(f"  ZIP Code: {profile.get('zip_code', 'None')}\n")
            f.write(f"  Address: {profile.get('address', 'None')}\n")
            f.write(f"  Representative Hash: {profile.get('hash', 'None')}\n")
            f.write("\n")

if __name__ == "__main__":
    input_file = r"Results/ohio-nc-dob_randall-attack_results.txt" 
    output_file = r"Profiles/ohio-nc-dob_randall-attack_profiles.txt"  
    consolidate_profiles(input_file, output_file)

# df_profiles = pd.DataFrame.from_dict(profiles, orient="index")
# df_profiles.to_csv(output_file, index_label="profile_key")