# Create a table using your table name, column names and column types, if not already in existence
def create_table_if_not_exists(cursor, table_name, column_names, column_data_types):
    """
    Create a table if it does not exist in the database with the given table name, column names, and data types.

    Parameters:
    - cursor (sqlite3.Cursor): The SQLite database cursor.
    - table_name (str): The name of the table to be created.
    - column_names (list of str): A list containing the names of the columns.
    - column_data_types (list of str): A list containing the data types of the corresponding columns.

    Example:
    ```
    # Define table name, column names, and data types
    table_name = 'crawler_data'
    columns = ['id', 'url', 'template_data', 'datetime_stamp', 'http_status']
    data_types = ['INTEGER PRIMARY KEY AUTOINCREMENT', 'TEXT', 'TEXT', 'TEXT', 'INTEGER']

    # Call the function to create the table
    create_table_if_not_exists(cursor, table_name, columns, data_types)
    ```

    In the example, this function would generate the following SQL query and execute it:
    ```sql
    CREATE TABLE IF NOT EXISTS crawler_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT,
        template_data TEXT,
        datetime_stamp TEXT,
        http_status INTEGER
    )
    ```
    """
    # Combine column names and data types into a list of strings
    columns_definition = [f"{name} {data_type}" for name, data_type in zip(column_names, column_data_types)]

    # Concatenate the column definitions into the SQL query
    query = f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            {', '.join(columns_definition)}
        )
    '''

    # Execute the SQL query
    cursor.execute(query)