import pandas as pd

import numpy as np

def standardize_all(data):
    """
    Standardize all columns in the dataset.

    Args:
    - data (list of lists): The data containing columns to standardize.

    Returns:
    - standardized_data (list of lists): The standardized data.
    """
    # Convert the data to a DataFrame
    df = pd.DataFrame(data)

    # Initialize a DataFrame to store the standardized data
    standardized_df = pd.DataFrame()

    # Iterate over each column in the DataFrame
    for col in df.columns:
        # Check if the column contains string values
        if df[col].dtype == object:
            # If it's a string column, keep it unchanged and add it to the standardized DataFrame
            standardized_df[col] = df[col]
        else:
            # If it's a numeric column, standardize it
            standardized_df[col] = (df[col] - df[col].mean()) / df[col].std()

    # Convert the standardized DataFrame back to a list of lists
    standardized_data = standardized_df.values.tolist()

    return standardized_data


def standardize_selected_columns(data, selected_columns):
    """
    Standardize (z-score) the selected columns in the data.

    Args:
    - data (list of lists): The data containing columns to standardize.
    - selected_columns (list of int): The indices of the columns to standardize.

    Returns:
    - standardized_data (list of lists): The standardized data.
    """
    # Initialize an empty list to store standardized data
    standardized_data = []

    # Iterate over each row in the data
    for row in data:
        # Initialize an empty list to store standardized values for the row
        standardized_row = []
        # Iterate over each column index
        for i, val in enumerate(row):
            # Check if the current column index is in the selected columns list
            if i in selected_columns:
                # Check if the value is numeric (int or float)
                if isinstance(val, (int, float)):
                    # Extract the column values using the current index i
                    column_values = [row[i] for row in data if isinstance(row[i], (int, float))]
                    # Compute mean and standard deviation of the column values
                    mean_val = sum(column_values) / len(column_values)
                    std_dev = (sum((x - mean_val) ** 2 for x in column_values) / len(column_values)) ** 0.5
                    # Standardize the value and append it to the standardized row
                    standardized_val = (val - mean_val) / std_dev
                    standardized_row.append(standardized_val)
                else:
                    # If the value is not numeric, append the original value to the standardized row
                    standardized_row.append(val)
            else:
                # If the column is not selected, append the original value to the standardized row
                standardized_row.append(val)
        # Append the standardized row to the list of standardized data
        standardized_data.append(standardized_row)

    return standardized_data
