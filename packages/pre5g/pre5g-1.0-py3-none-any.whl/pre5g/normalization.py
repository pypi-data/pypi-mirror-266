
import pandas as pd
def normalize_all(data):
    """
    Normalize all columns in the dataset, retaining string values.

    Args:
    - data (list of lists): The data containing columns to normalize.

    Returns:
    - normalized_data (list of lists): The normalized data.
    """
    normalized_data = []
    for column in data:
        if all(isinstance(x, (int, float)) for x in column):  # Check if all values are numeric
            min_val = min(column)
            max_val = max(column)
            if max_val - min_val == 0:
                normalized_column = column[:]  # Preserve original values if range is 0
            else:
                normalized_column = [(x - min_val) / (max_val - min_val) for x in column]
        else:
            normalized_column = column[:]  # Preserve string values
        normalized_data.append(normalized_column)
    return normalized_data


def normalize_selected_columns(data, selected_columns):
    """
    Normalize the selected columns in the data.
    
    Args:
    - data (list of lists): The data containing columns to normalize.
    - selected_columns (list of int): The indices of the columns to normalize.
    
    Returns:
    - normalized_data (list of lists): The normalized data.
    """
    # Initialize an empty list to store normalized data
    normalized_data = []
    
    # Iterate over each row in the data
    for row in data:
        # Initialize an empty list to store normalized values for the row
        normalized_row = []
        # Iterate over each column index
        for i, val in enumerate(row):
            # Check if the current column index is in the selected columns list
            if i in selected_columns:
                # Check if the value is numerical
                if isinstance(val, (int, float)):
                    # Extract the column values using the current index i
                    column_values = [row[i] for row in data]
                    # Normalize the value and append it to the normalized row
                    min_val = min(column_values)
                    max_val = max(column_values)
                    normalized_val = (val - min_val) / (max_val - min_val)
                    normalized_row.append(normalized_val)
                else:
                    # If the value is not numerical (i.e., a string), append it directly
                    normalized_row.append(val)
            else:
                # If the column is not selected, append the original value to the normalized row
                normalized_row.append(val)
        # Append the normalized row to the list of normalized data
        normalized_data.append(normalized_row)
    
    return normalized_data
