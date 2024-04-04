# __init__.py

# Import any modules or symbols needed for printing the AIML code files
import os

# Define the directory path where the AIML code files are located
AIML_CODE_DIR = '/Users/sharathchandrak/Desktop/avi_package-main/lab'

# Function to print the contents of AIML code files
def print_aiml_code_file(filename):
    file_path = os.path.join(AIML_CODE_DIR, filename)
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            print(f"Contents of {filename}:")
            print(file.read())
    else:
        print(f"File {filename} does not exist.")
def Print(filename):
    print_aiml_code_file(filename)
# Example usage:
Print('p1.py') 
