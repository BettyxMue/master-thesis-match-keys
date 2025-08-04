# Update the generate_profile_key function to include date_of_birth in the key
def generate_profile_key(first_name, last_name, year_of_birth, date_of_birth=None):
    if date_of_birth:
        return f"{first_name.lower()}_{last_name.lower()}_{year_of_birth}_{date_of_birth}"
    return f"{first_name.lower()}_{last_name.lower()}_{year_of_birth}"

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
            print(f"Conflict in day of birth for {existing_profile['first_name']} {existing_profile['last_name']}: "
                  f"{existing_profile['date_of_birth']} vs {new_data['date_of_birth']}")
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
            if line.startswith("Matched values for"):
                current_match_key = line.split("(")[0].split()[-1]
                continue

            # Parse hash and plain text values
            if line.startswith("Hash:"):
                parts = line.split("←")
                hash_val = parts[0].split("Hash:")[1].strip()
                plain_values = eval(parts[1].split("Values:")[1].strip())  # Convert string tuple to actual tuple

                # Handle different match key formats
                if len(plain_values) == 4:  # Format: (first_name, last_name, year_of_birth, day_of_birth)
                    first_name, last_name, year_of_birth, date_of_birth = plain_values
                    date_of_birth = f"{year_of_birth}-{date_of_birth}"  # Construct full date of birth in yyyy-mm-dd format
                    key = generate_profile_key(first_name, last_name, year_of_birth, date_of_birth)
                    new_data = {
                        "first_name": first_name,
                        "last_name": last_name,
                        "year_of_birth": year_of_birth,
                        "date_of_birth": date_of_birth,  # Store full date of birth
                        "hash": hash_val,  # Add the hash as the representative hash
                    }
                elif len(plain_values) == 3:  # Format: (first_name, last_name, dob or year_of_birth)
                    first_name, last_name, third_value = plain_values
                    if "-" in third_value:  # Likely a full DOB (yyyy-mm-dd)
                        dob = third_value
                        year_of_birth = dob.split("-")[0]  # Extract year from DOB
                        key = generate_profile_key(first_name, last_name, year_of_birth, dob)
                        new_data = {
                            "first_name": first_name,
                            "last_name": last_name,
                            "year_of_birth": year_of_birth,
                            "date_of_birth": dob,  # Use full DOB
                            "hash": hash_val,  # Add the hash as the representative hash
                        }
                    elif third_value.isdigit() and len(third_value) == 4:  # Likely a year of birth (yyyy)
                        year_of_birth = third_value
                        key = generate_profile_key(first_name, last_name, year_of_birth)
                        new_data = {
                            "first_name": first_name,
                            "last_name": last_name,
                            "year_of_birth": year_of_birth,
                            "date_of_birth": None,  # Date of birth not available
                            "hash": hash_val,  # Add the hash as the representative hash
                        }
                    else:
                        print(f"Unknown format for match key {current_match_key}: {plain_values}")
                        continue
                elif len(plain_values) == 2:  # Format: (first_name, last_name, dob or year_of_birth)
                    last_name, third_value = plain_values
                    if "-" in third_value:  # Likely a full DOB (yyyy-mm-dd)
                        dob = third_value
                        year_of_birth = dob.split("-")[0]  # Extract year from DOB
                        key = generate_profile_key(first_name, last_name, year_of_birth, dob)
                        new_data = {
                            "first_name": first_name,
                            "last_name": last_name,
                            "year_of_birth": year_of_birth,
                            "date_of_birth": dob,  # Use full DOB
                            "hash": hash_val,  # Add the hash as the representative hash
                        }
                    elif third_value.isdigit() and len(third_value) == 4:  # Likely a year of birth (yyyy)
                        year_of_birth = third_value
                        key = generate_profile_key(first_name, last_name, year_of_birth)
                        new_data = {
                            "first_name": first_name,
                            "last_name": last_name,
                            "year_of_birth": year_of_birth,
                            "date_of_birth": None,  # Date of birth not available
                            "hash": hash_val,  # Add the hash as the representative hash
                        }
                    else:
                        print(f"Unknown format for match key {current_match_key}: {plain_values}")
                        continue
                else:
                    print(f"Unknown format for match key {current_match_key}: {plain_values}")
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
            f.write(f"  First Name: {profile['first_name']}\n")
            f.write(f"  Last Name: {profile['last_name']}\n")
            f.write(f"  Year of Birth: {profile['year_of_birth']}\n")
            f.write(f"  Date of Birth: {profile.get('date_of_birth', 'None')}\n")  # Use .get() to handle missing keys
            f.write(f"  Representative Hash: {profile['hash']}\n")
            f.write("\n")

if __name__ == "__main__":
    input_file = r"Results/ohio-nc-dob_randall-attack_results.txt" 
    output_file = r"Profiles/ohio-nc-dob_randall-attack_profiles.txt"  
    consolidate_profiles(input_file, output_file)