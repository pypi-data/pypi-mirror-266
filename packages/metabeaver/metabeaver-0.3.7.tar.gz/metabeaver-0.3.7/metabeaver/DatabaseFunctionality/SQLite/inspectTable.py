import sqlite3
import sys

def getRowsAndSummary(cursor, table_name, n):
    """
    Fetch the first n rows from an SQLite table, print column names, column types, and calculate total memory.

    Parameters:
    - cursor (sqlite3.Cursor): The SQLite database cursor.
    - table_name (str): The name of the table to fetch rows from.
    - n (int): The number of rows to fetch.

    Returns:
    - rows (list of tuples): The first n rows from the table.
    """

    # Fetch the first n rows from the table
    cursor.execute(f'SELECT * FROM {table_name} LIMIT {n}')
    rows = cursor.fetchall()

    # Get column information
    column_info = cursor.execute(f'PRAGMA table_info({table_name})').fetchall()

    # Print column names
    column_names = [info[1] for info in column_info]
    print("Column Names:", column_names)

    # Print column types
    column_types = [info[2] for info in column_info]
    print("Column Types:", column_types)

    # Print the first n rows
    print(f"\nFirst {n} Rows:")
    for row in rows:
        print(row)

    # Calculate total memory
    total_memory = sum(sys.getsizeof(cell) for row in rows for cell in row)
    print(f"\nTotal Memory of the First {n} Rows: {total_memory} bytes")

    return rows

# Example usage
#conn = sqlite3.connect('your_database.db')  # Replace 'your_database.db' with your actual database name/path
conn = sqlite3.connect('C:\\Users\\lukep\\PycharmProjects\\PolyLLM\\crawler_data.db')
cursor = conn.cursor()
table_name = 'scrapy'  # Replace 'your_table' with your actual table name
n = 10  # Number of rows to fetch

# Run function to SQLite db to fetch n rows from the desired table.
fetched_rows = getRowsAndSummary(cursor, table_name, n)

# Close the connection
conn.close()

























