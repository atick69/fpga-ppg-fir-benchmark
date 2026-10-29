from kaggle.api.kaggle_api_extended import KaggleApi
import os

# 1. Authenticate
api = KaggleApi()
api.authenticate()
print("Authentication successful!")

# 2. Use the NEW working dataset slug
dataset_slug = 'antonjuk/wearable-ppg-acc-and-ecg-heart-rate-dataset'
download_path = './data'

# Create the data directory if it doesn't exist
os.makedirs(download_path, exist_ok=True)

# 3. Download and unzip
print(f"Downloading {dataset_slug}... This might take a minute.")
api.dataset_download_files(dataset_slug, path=download_path, unzip=True)

print(f"Success! Data downloaded and unzipped into the '{download_path}' folder.")