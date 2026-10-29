import os

print("Scanning for data files...")
for root, dirs, files in os.walk('./data'):
    for file in files:
        file_path = os.path.join(root, file)
        print(f"Found: {file_path}")