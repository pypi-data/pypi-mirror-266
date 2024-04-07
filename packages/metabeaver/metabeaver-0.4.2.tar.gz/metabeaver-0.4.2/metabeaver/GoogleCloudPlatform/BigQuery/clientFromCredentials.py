import json

from google.cloud import bigquery
from google.oauth2 import service_account

import yaml

from typing import List
import pandas as pd


# Return a credentials via supplying a service_account.Credentials with valid credential.json loc GCP API calls
def get_credentials_from_yaml(yaml_file_path, cloud_platform, service_json_filepath):

    # Attempt to load a service_account.Credentials from a YAML file reference to stored location."""
    try:
        # Try to load the YAML file
        with open(yaml_file_path, 'r') as yaml_file:
            config = yaml.safe_load(yaml_file)

        # Extract path to service account JSON file from YAML config
        credentials_path = config[cloud_platform][service_json_filepath]

        # Load service account credentials from JSON file and return the credentials to be used in API calls.
        credentials = service_account.Credentials.from_service_account_file(credentials_path)
        return credentials
    # Print any Exception associated with retrieval.
    except Exception as e:
        print(f"Error: {e}")


# Create a bigquery client from a credentials.json
def get_bigquery_client_from_json(credentials_path='path/to/your/credentials.json'):
    # Example usage with explicit credentials file path
    # bigquery_client = get_bigquery_client(r'C:\Users\lukep\OneDrive\workandplay\credentials.json')

    # Explicitly provide the path to your service account key file
    credentials = service_account.Credentials.from_service_account_file(credentials_path)

    # Create a BigQuery client using the provided credentials
    client = bigquery.Client(credentials=credentials)

    return client


# Assumes existence of a yaml file with a valid path to credentials.json and gcp project name
def get_bigquery_client_from_yaml(config_file_path: str) -> bigquery.Client:
    """
    Load GCP credentials from a YAML configuration file and create a BigQuery client.

    :param config_file_path: Path to the YAML configuration file.
    :return: BigQuery client object.
    """

    # Load configuration from YAML file
    with open(config_file_path, 'r') as file:
        configuration = yaml.safe_load(file)

    # Get the credentials file location and project name from configuration
    credentials_path = configuration['GCP']['credentials_file_loc']
    gcp_project = configuration['GCP']['project_name']

    # Load credentials from the specified JSON file
    with open(credentials_path, 'r') as file:
        credentials_info = json.load(file)

    # Create a BigQuery client using the loaded credentials
    client = bigquery.Client.from_service_account_info(
        credentials_info,
        project=gcp_project
    )

    # Returns a client we can use to interact with BigQuery.
    return client


def create_bigquery_client(credentials_path):
    """Create a BigQuery client using service account credentials."""
    try:
        # Load service account credentials from JSON file
        credentials = service_account.Credentials.from_service_account_file(credentials_path)

        # Create BigQuery client with the loaded credentials
        client = bigquery.Client(credentials=credentials)

        return client
    except Exception as e:
        print(f"Error creating BigQuery client: {e}")
        return None