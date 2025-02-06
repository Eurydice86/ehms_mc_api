from google.cloud import storage
import os
os.environ["GCLOUD_PROJECT"] = "ehms-424721"

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name, if_generation_match=None)

if __name__ == "__main__":
    upload_blob("ehms-myclub", "test.txt", "test.txt")
