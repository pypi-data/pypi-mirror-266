import numpy as np
import time


# Filters a dataframe down to rows where, in a given column, column-row cell values start with the string
def filterOnSubstringMorpheme(df, #DataFrame to filter
                              column_name, #Column to filter on
                              substring, # Substring to filter out row is column values start or end with
                              morphemeType='prefix', # Default argument to filter strings that start with substring
                              chattyBeaver=True,  # Whether to print the runtime of the function
                              ):
    """
    Filter the DataFrame to include only rows where the specified column's values start with the given substring.

    Args:
        df (pd.DataFrame): The DataFrame to filter.
        column_name (str): The name of the column to filter on.
        substring (str): The substring to match at the beginning of the column values.

    Returns:
        pd.DataFrame: The filtered DataFrame.
    """
    start_time = time.time()

    # Use numpy to create a boolean mask for rows where the column starts with the substring
    if morphemeType == 'prefix':
        mask = np.array([str(val).startswith(substring) for val in df[column_name]])
    else:
        mask = np.array([str(val).endswith(substring) for val in df[column_name]])

    # Apply the mask to the DataFrame
    filtered_df = df[mask]

    # Print the runtime of filtering out the results that started or ended with the target substring
    if chattyBeaver:
        end_time = time.time()
        execution_time = end_time - start_time
        print("Execution time:", execution_time, "seconds")

    return filtered_df