import sys
import os
import sys
import os
from vertexai.language_models import CodeGenerationModel
from google.oauth2 import service_account
import vertexai
import re
import json
import time
import requests
from dotenv import load_dotenv
from google.cloud import storage
from concurrent import futures
import shutil
import zipfile
import threading

# Load environment variables from .env file
credentials_data={
  "type": "service_account",
  "project_id": "symbolic-bit-398912",
  "private_key_id": "6cc13a1aa736855f25148aa6daa2f99374307180",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQClM+Eub91x2IhM\nMw5sID2+JwvHI9cRtE5BpIq13BXlN87z8gnKDUIfRQslGpg2pIk+IvizweKy8lmq\nOrA7XPLVFQl3JEvzq9xKbMAaLoOUS6rOf9ik157TPDw+m3JnL4VwNrjhplqWbU+X\nmCXc1hxdX2cm5SM2VZUE5vgco32/IKKvv511E6JUQSeFzB95/4XKkPO2xADcmams\n+6ngxJMRkuF6u1DZyWFkpCzYB/gCaX+HnHEiPm3doYOdb+i3fXuVBZ5y0V2zEcpz\nZeDpbZO7hmWQxPOnjCLWHbqIeCJreDbDdHMelkyv67g1Q9NRwTCLb8RfmeGzMvTo\nv9KJkr0pAgMBAAECggEAARo3hnfN99SEvv1tkIsmiP5PCyUnakF/GYZfkUHGuPYx\nC1pcy7G1nz/MCJNaMK3TEfcUcclOxKLutj7DWPdl0huHKfm0CAw9jBbtsT8I4b8f\nhKvrENk01h6wyDor/pmdP60dzrkCzGjY/x9PdrR3EVMcUnDKVgfRgWwz0P0bpGAw\nnrl6OkOMlQX2Psk0ekWI/WS5Tvt4G3P5VJNeoOdtRQEKvR+qaR3CIJyGafX0RrE8\n0PT2bYUeRP3A2+p1Si7Y6j3E/Kor+mwOjzro2Yl5eANwZMc3sYRxB3hKKAv5StNB\njU804hfJkfMGn46yy1altAUG9s9bq4P+qllgko7+AQKBgQDhrtm/JUAoUh7ew3c6\n89L5rtqZIdZkDoyTFEqQEhu1pN+RILL5J5TLtACmCzBFnW0VNfh0B5bDCuRlstoU\nNK5bdeeQmmeZmP617XB4rakKw0yrOMdu77+RMaGPegVr/bs5xgQjPg5iOrxIEL0r\nduaWYVp5wjW+YksFzmGEu1NIlQKBgQC7ZSIwahplYWzb1WKXj+wy+rWNfEce/yyh\nM5lfHEknUZdd6cu8s6rhkjVEkIeO5OFiylr7pqDEH/5gD6r6YSr4db25sFH5m51u\nsl3yHk9Dam0AdeBdQ21rc1Khfl8ycuFzSwsgSYEWtZ3uoWkud6spxiS3Mqp9uz+i\nBgz75Fs5RQKBgBvSITemEO2nifSuJfGXgyeSfZIpELPO81diRfrSsKXIyGKspEOA\ntKAT9YyCjpXWXU8jExjCorwyiItc6/NXtzLBKyWxUxolOSkWNyo5RkB0aOwmmLc9\nSOFOO/ti8G4qnjz2AyaRDNbhJLrBjYBhLPXW1H90CIoKtfLmSTFConatAoGBAIfH\nDk+gAUIlphdedBI28MA7UWKTgoCeCTs/xMfaGdMIVjFwnfM7Bvxr0Ha+dcn+YqQO\n1H9zyxZvzALUN2E1GEpwHSi27Z56t0YmrNUqSuog6ZukzQ0mNtjc9SkYBGfsPxgn\nbodVWtgWfbkScMB/aqBY9e9bIZb6HnAKDExSuBo1AoGAJnAsYFHyeDs8ZFaVGhPO\nGeYXTMj9JGwZHR+wqFfuiBIqs/cra3xETIDyr6cGT9xTjQ0nVazvROBANgkU+YIO\nWxzzc77PnpfP20yMMTNsJFoZhSQUns8LY9hxzKSnPYURqf32HTTImmmCbz2RJAyO\nOvPWkmJDkDvalolS6HNnEPE=\n-----END PRIVATE KEY-----\n",
  "client_email": "vertex-ai-service-account@symbolic-bit-398912.iam.gserviceaccount.com",
  "client_id": "114836232517254252283",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/vertex-ai-service-account%40symbolic-bit-398912.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}
credentials = service_account.Credentials.from_service_account_info(credentials_data)

vertexai.init(
    project="symbolic-bit-398912",
    location="us-central1",
    credentials=credentials
)
def create_bucket(bucket_name):
    """Create a new Google Cloud Storage bucket if it doesn't already exist."""
    storage_client = storage.Client(credentials=credentials)

    # Check if the bucket exists
    bucket = storage_client.bucket(bucket_name)
    if not bucket.exists():
        # Create the bucket
        bucket.create()
        # print(f'Bucket {bucket.name} created.')
    else:
        # print(f'Bucket {bucket.name} already exists.')
        pass
        
def upload_file(bucket_name, local_file_path, relative_path):
    """Upload a single file to Google Cloud Storage bucket."""
    storage_client = storage.Client(credentials=credentials)
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(relative_path)
    blob.upload_from_filename(local_file_path)

    

def zip_directory_with_exclusions(directory):
    def zip_directory(directory, zip_file):
        with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(directory):
                if 'node_modules' in dirs:
                    dirs.remove('node_modules')  # Skip node_modules directory and its contents
                    continue
                if '.git' in dirs:
                    dirs.remove('.git')  # Skip .git directory and its contents
                    continue
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, directory))

    zip_filename = os.path.basename(directory) + ".zip"  # Name of the zip file will be the current directory name

    # Create a temporary directory to copy files, excluding node_modules and .git
    temp_dir = os.path.join(directory, "__temp_zip_dir__")
    shutil.copytree(directory, temp_dir, ignore=shutil.ignore_patterns('node_modules', '.git', zip_filename))

    # Animation: Print "Training started" with animation dots
    

    zip_directory(temp_dir, zip_filename)

    # Clean up the temporary directory
    shutil.rmtree(temp_dir)

    if os.path.getsize(zip_filename) <= 0:
        print("Error in training ")
    

def animate_training():
    # Print "Training started" with animation
    sys.stdout.write("Training Started")
    sys.stdout.flush()
    while not animation_stop_event.is_set():
        for _ in range(3):
            sys.stdout.write(".")
            sys.stdout.flush()
            time.sleep(0.5)  # Adjust speed of animation
        sys.stdout.write("\b" * 3)  # Move cursor back to delete dots
        sys.stdout.flush()
        time.sleep(0.5)  # Pause before restarting animation

def start_animation():
    animate_training()
    print()  # Add a newline after animation
    sys.exit()

def start():
    """Entry point for the 'gocodeo-train start' command."""
    global animation_stop_event
    animation_stop_event = threading.Event()

    # Fetch the current working directory
    current_dir = os.getcwd()

    # Extract the directory name from the current directory path
    dir_name = os.path.basename(os.path.normpath(current_dir))

    # Sanitize the directory name to adhere to bucket naming rules
    bucket_name = dir_name.lower().replace(" ", "-")

    # Ensure the bucket name meets length requirements
    bucket_name = bucket_name[:63]+"-gocodeo"
    # print(bucket_name)

    # Create the bucket
    create_bucket(bucket_name)

    # Start animation thread
    animation_thread = threading.Thread(target=start_animation)
    animation_thread.start()

    # Create a zip file of the directory contents
    zip_file_path = os.path.join(current_dir, f'{dir_name}.zip')

    # Zip the directory contents
    zip_directory_with_exclusions(current_dir)

    # Stop animation
    
    animation_stop_event.set()
    animation_thread.join()
    # Upload the zip file to the bucket
    upload_file(bucket_name, zip_file_path, f'{dir_name}.zip')

    # Remove the zip file from the local filesystem
    os.remove(zip_file_path)
    
    print("Training Completed")

if __name__ == "__main__":
    start()