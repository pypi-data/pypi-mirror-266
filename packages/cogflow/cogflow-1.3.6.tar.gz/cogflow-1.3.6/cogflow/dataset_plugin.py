"""
This module provides functionality related to Dataset upload via plugin.
"""

import io
import os
import requests
from minio import Minio


class DatasetPlugin:
    """
    A class to handle dataset-related operations.

    Attributes:
        None
    """

    def __init__(self):
        """
        Initializes DatasetPlugin with environment variables.
        """
        # Retrieve MinIO connection details from environment variables
        self.minio_endpoint = os.getenv("MINIO_ENDPOINT")
        self.minio_access_key = os.getenv("MINIO_ACCESS_KEY")
        self.minio_secret_key = os.getenv("MINIO_SECRET_KEY")
        self.minio_bucket_name = os.getenv("MINIO_BUCKET_NAME")

    def query_endpoint_and_download_file(self, url, output_file):
        """
        Queries an endpoint and downloads a file from it.

        Args:
            url (str): The URL of the endpoint.
            output_file (str): The name of the output file to save.

        Returns:
            tuple: A tuple containing a boolean indicating success and the file URL if successful.
        """
        try:
            response = requests.get(url)
            if response.status_code == 200:
                file_url = self.save_to_minio(response.content, output_file)
                return True, file_url
            print(f"Request failed with status code {response.status_code}")
            raise Exception("Request couldnot be successful due to error")

        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            raise Exception("Exception occurred during the requested operation")

    def save_to_minio(self, file_path, output_file):
        """
        Saves a file to MinIO.

        Args:
            file_path (bytes): The content of the file to be uploaded.
            output_file (str): The name of the file to be uploaded.

        Returns:
            str: The presigned URL of the uploaded file.
        """

        # Initialize MinIO client
        minio_client = Minio(
            self.minio_endpoint,
            access_key=self.minio_access_key,
            secret_key=self.minio_secret_key,
            secure=False,
        )  # Change to True if using HTTPS
        object_name = output_file

        # Check if the bucket exists, if not, create it
        bucket_exists = minio_client.bucket_exists(self.minio_bucket_name)
        if not bucket_exists:
            try:
                minio_client.make_bucket(self.minio_bucket_name)
                print(f"Bucket '{self.minio_bucket_name}' created successfully.")
            except Exception:
                print(f"Bucket '{self.minio_bucket_name}' already exists.")
        # Put file to MinIO
        try:
            content_bytes = io.BytesIO(file_path).read()
            # Upload content to MinIO bucket
            minio_client.put_object(
                self.minio_bucket_name,
                object_name,
                io.BytesIO(content_bytes),
                len(content_bytes),
            )
            print(
                f"File {output_file} uploaded successfully to MinIO bucket"
                f" {self.minio_bucket_name} as {object_name}."
            )
            presigned_url = minio_client.presigned_get_object(
                self.minio_bucket_name, object_name
            )
            print(f"Access URL for '{object_name}': {presigned_url}")
            return presigned_url
        except Exception as err:
            print(f"Error uploading file: {err}")
            raise Exception(f"Error uploading file: {err}")
