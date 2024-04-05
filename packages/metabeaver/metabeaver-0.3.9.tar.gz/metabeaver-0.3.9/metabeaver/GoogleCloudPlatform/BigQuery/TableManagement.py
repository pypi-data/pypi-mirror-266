# Rename the get crawled pages as it can be much more generic

import datetime as dt
import pandas as pd
import numpy as np
import yaml
from typing import List
from google.auth.credentials import Credentials
from google.cloud import bigquery
from google.oauth2 import service_account


# Given valid client, details for the table location, and a schema, this function will create a table in BigQuery.
def create_bigquery_table(client, tableset, table_name, schema):
    """Creates a BigQuery table in the specified tableset with the given table name and schema.

    Args:
        client (google.cloud.bigquery.client.Client): The BigQuery client to use for creating the table.
        tableset (str): The dataset ID where the table will be created.
        table_name (str): The name for the new BigQuery table.
        schema (list[google.cloud.bigquery.SchemaField]): The schema for the new BigQuery table.

    Returns:
        google.cloud.bigquery.table.Table: The newly created BigQuery table.
    """
    try:
        # Get a reference to the table
        table_ref = client.dataset(tableset).table(table_name)

        # Create the table object
        table = bigquery.Table(table_ref, schema=schema)

        # Create the table in BigQuery
        table = client.create_table(table)

        # Return the new table object
        return table
    except Exception as e:
        print(f"Error creating table '{table_name}' in dataset '{tableset}': {e}")


# Maps Python primitive types and numpy/panda types to BigQuery equivalents
def create_schema(items: List, field_names: List[str]) -> List[bigquery.SchemaField]:
    """
    Creates a BigQuery schema based on a list of items.

    :param items: List of items to determine schema from.
    :param field_names: List of field names for each item in the list.
                        If not specified, default names are used.
    :return: List of BigQuery schema fields.
    """
    # Define a mapping between Python and BigQuery types
    type_map = {
        int: 'INTEGER',
        float: 'FLOAT',
        str: 'STRING',
        bool: 'BOOLEAN',
        bytes: 'BYTES',
        bytearray: 'BYTES',
        memoryview: 'BYTES',
        'Int64': 'INTEGER',
        'Float64': 'FLOAT',
        pd.Timestamp: 'TIMESTAMP',
        pd.DateOffset: 'DATE',
        pd.Timedelta: 'TIME',
        pd.Interval: 'STRING',  # Can't directly map to BigQuery type, so using STRING as a placeholder
        pd.CategoricalDtype: 'STRING',  # Can't directly map to BigQuery type, so using STRING as a placeholder
        np.float16: 'FLOAT',
        np.float32: 'FLOAT',
        np.float64: 'FLOAT',
        np.int8: 'INTEGER',
        np.int16: 'INTEGER',
        np.int32: 'INTEGER',
        np.int64: 'INTEGER',
        np.uint8: 'INTEGER',
        np.uint16: 'INTEGER',
        np.uint32: 'INTEGER',
        np.uint64: 'INTEGER',
    }

    # Create an empty list to hold the schema fields
    schema = []

    # Iterate over each item in the list
    for idx, item in enumerate(items):
        # Get the type of the current item
        field_type = type(item)
        # Look up the corresponding BigQuery type in the type map
        bq_type = type_map.get(field_type, 'STRING')
        # Get the field name for the current item
        field_name = field_names[idx] if idx < len(field_names) else f'field_{idx}'
        # Create a new schema field with the determined type and name
        schema.append(bigquery.SchemaField(name=field_name, field_type=bq_type))

    return schema


# Takes a pandas dataframe and creates a BigQuery table in target location, with an automatically determined schema.
def create_bigquery_table_from_dataframe(client: bigquery.Client,
                                         dataset_id: str,
                                         table_name: str,
                                         dataframe: pd.DataFrame):
    """
    Create a BigQuery table from a Pandas DataFrame.

    :param client: BigQuery client object.
    :param dataset_id: ID of the dataset where the table will be created.
    :param table_name: Name of the table to be created.
    :param dataframe: Pandas DataFrame containing the data.
    """
    # Generate BigQuery schema from DataFrame columns
    schema = create_schema(dataframe.values[0], dataframe.columns.tolist())

    # Create BigQuery table
    create_bigquery_table(client, client.project, dataset_id, table_name, schema)


def create_bq_table_from_df_with_credentials(credentials: Credentials,
                                         dataset_id: str,
                                         table_name: str,
                                         dataframe: pd.DataFrame):
    """
    Create a BigQuery table from a Pandas DataFrame.

    :param credentials: Google Cloud credentials object.
    :param dataset_id: ID of the dataset where the table will be created.
    :param table_name: Name of the table to be created.
    :param dataframe: Pandas DataFrame containing the data.
    """
    #
    try:
        # Create BigQuery client with provided credentials
        client = bigquery.Client(credentials=credentials)

        # Generate BigQuery schema from DataFrame columns
        schema = create_schema(dataframe.iloc[0], dataframe.columns.tolist())

        # Create BigQuery table
        create_bigquery_table(client, client.project, dataset_id, table_name, schema)
        print(f"Table '{table_name}' created successfully in dataset '{dataset_id}'.")
    #
    except Exception as e:
        print(f"Error creating table: {e}")


# Gets the most up to date data for a table where the target column has an entries within the last n_days
def get_valid_pages(client, dataset_name, table_name, target_column, date_column, n_days=30, end_date=None):

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


