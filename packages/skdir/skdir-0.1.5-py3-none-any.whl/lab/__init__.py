import os

# Define the directory path where the AIML code files are located
AIML_CODE_DIR = '/Users/sharathchandrak/Desktop/avi_package-main/lab'

# Function to print the contents of all AIML code files
def print_all_aiml_code_files():
    for filename in os.listdir(AIML_CODE_DIR):
        if filename.endswith(".py"):
            file_path = os.path.join(AIML_CODE_DIR, filename)
            with open(file_path, 'r') as file:
                print(f"Contents of {filename}:")
                print(file.read())

# Example usage:
print_all_aiml_code_files()
