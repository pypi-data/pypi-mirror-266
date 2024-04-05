import datetime as dt
import json
import pandas as pd
import yaml
from google.cloud import bigquery


# Assume a config-yaml file with valid GCP credentials.json filepath, used to get X rows of data.
def getData(x):

    # Get the credentials for the API calls
    with open('config-yaml.yaml', 'r') as file:
        configuration = yaml.safe_load(file)

    # Get the path of the credentials and the project name for dynamically requesting a GCP BigQuery client
    credentials_path = configuration['GCP']['credentials_file_loc']
    gcp_project = configuration['GCP']['project_name']

    # Load the credentials from the file path location specified in the yaml.
    with open(credentials_path, 'r') as file:
        credentials_info = json.load(file)

    # Use the 'from_service_account_info' method to dynamically load credentials from a file
    client = bigquery.Client.from_service_account_info(
        credentials_info,
        project=gcp_project
    )

    # Get the first x rows from the table.
    df = get_first_n_rows(client,
                          configuration['GCP']['project_name'],
                          configuration['GCP']['dataset'],
                          configuration['GCP']['table_name'],
                          x)

    return df


# Fetches the first n rows from a bigquery table. Must receive a valid instantiated client
def get_first_n_rows(client, project_id, dataset_id, table_id, n):
    """
    Fetch the first n rows from the specified BigQuery table.

    Args:
        client (google.cloud.bigquery.Client): A valid BigQuery client.
        project_id (str): Google Cloud project ID.
        dataset_id (str): BigQuery dataset ID.
        table_id (str): BigQuery table ID.
        n (int): The number of rows to fetch.

    Returns:
        list: A list of rows retrieved from the table.
    """
    # Construct the fully-qualified table ID
    table_ref = client.dataset(dataset_id, project=project_id).table(table_id)

    # Get the table, the table schema, and the schema fields
    table = client.get_table(table_ref)
    schema = table.schema
    schema_fields = [field.name for field in schema]

    # Construct the SQL query to get the first n rows.
    if n != float('inf'):
        query = f"SELECT * FROM `{table_ref}` LIMIT {n}"
    # If the limit value would have been infinity, return all records.
    else:
        query = f"SELECT * FROM `{table_ref}`"

    # Execute the query
    query_job = client.query(query)

    # Fetch the results
    results = query_job.result()

    # Convert the results to a list of rows
    rows = list(results)
    df = pd.DataFrame(data=[list(row.values()) for row in rows], columns=schema_fields)

    return df


# Gets the data within the last n_days if the table has any entries within the last n_days, and a date_column to check.
def get_recent_rows(client, dataset_name, table_name, target_column, date_column, n_days=30, end_date=None):

    try:
        # Get current time in UTC
        now_utc = dt.datetime.utcnow()

        # Calculate start time based on specified number of days
        start_time = now_utc - dt.timedelta(days=n_days)

        # If end_date is not specified, use current time
        if end_date is None:
            end_date = now_utc

        # Initialize BigQuery client and get table reference
        table_ref = client.dataset(dataset_name).table(table_name)

        # Build query to retrieve latest valid crawl for each distinct entry in target column
        query = f"""
            SELECT *
            FROM (
                SELECT *,
                    ROW_NUMBER() OVER (
                        PARTITION BY {target_column}, DATE({date_column})
                        ORDER BY {date_column} DESC
                    ) AS row_num
                FROM {table_ref}
                WHERE LENGTH(COALESCE({target_column}, '')) > 0
                    AND {date_column} BETWEEN TIMESTAMP('{start_time.isoformat()}') AND TIMESTAMP('{end_date.isoformat()}')
            )
            WHERE row_num = 1
        """

        # Execute query and return results as an google.cloud.bigquery.table.RowIterator object
        results = client.query(query).result()

        # Convert the google.cloud.bigquery.table.RowIterator to a pandas dataframe. Start by converting to a dict.
        rows = [dict(row) for row in results]
        # Now we have a list of dicts, make a dataFrame
        results_df = pd.DataFrame.from_records(rows)

        # Return the results_df
        return results_df
    # Warn wherein we could not retrieve results within the last n_days
    except Exception as e:
        print(f'Tried retrieving data for {dataset_name}.{table_name}!')
        print(f'Got an exception: {str(e)}')