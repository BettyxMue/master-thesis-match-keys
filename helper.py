import os

# Directory containing the Ohio voter text files
input_directory = "ohiovoter/"  # Replace with the actual path
output_file = "ohio_voter.txt"

# Open the output file in write mode
with open(output_file, "w", encoding="utf-8") as outfile:
    # Iterate through all files in the input directory
    for filename in os.listdir(input_directory):
        # Check if the file is a text file
        if filename.endswith(".txt"):
            file_path = os.path.join(input_directory, filename)
            print(f"Processing file: {file_path}")
            
            # Try reading the file with utf-8 encoding, fallback to ISO-8859-1 if it fails
            try:
                with open(file_path, "r", encoding="utf-8") as infile:
                    outfile.write(infile.read())
            except UnicodeDecodeError:
                print(f"UnicodeDecodeError for file {file_path}. Trying ISO-8859-1 encoding.")
                with open(file_path, "r", encoding="ISO-8859-1") as infile:
                    outfile.write(infile.read())
            
            # Add a newline between files for separation
            outfile.write("\n")

print(f"All files have been combined into {output_file}")