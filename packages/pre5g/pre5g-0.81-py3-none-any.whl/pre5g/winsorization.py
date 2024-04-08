
import numpy as np

def winsorize_data(data, selected_columns, lower_pct=5, upper_pct=95):
    """
    Apply Winsorization to selected columns of the dataset.

    Parameters:
        data (list of lists): The input data where each inner list represents a row of data.
        selected_columns (list of int): The indices of the columns to which Winsorization should be applied.
        lower_pct (float): The lower percentile threshold (default is 5).
        upper_pct (float): The upper percentile threshold (default is 95).

    Returns:
        list of lists: The data with Winsorization applied to selected columns.
    """
    # Initialize an empty list to store winsorized data
    winsorized_data = []

    # Iterate over each row in the data
    for row in data:
        # Initialize an empty list to store winsorized values for the row
        winsorized_row = []
        # Iterate over each column index
        for i, val in enumerate(row):
            # Check if the current column index is in the selected columns list
            if i in selected_columns:
                # Check if the value is numeric (int or float)
                if isinstance(val, (int, float)):
                    # Extract the column values using the current index i
                    column_values = [row[i] for row in data if isinstance(row[i], (int, float))]
                    # Calculate percentile values
                    lower_value = np.percentile(column_values, lower_pct)
                    upper_value = np.percentile(column_values, upper_pct)
                    # Winsorize the value and append it to the winsorized row
                    if val < lower_value:
                        winsorized_val = lower_value
                    elif val > upper_value:
                        winsorized_val = upper_value
                    else:
                        winsorized_val = val
                    winsorized_row.append(winsorized_val)
                else:
                    # If the value is not numeric, append the original value to the winsorized row
                    winsorized_row.append(val)
            else:
                # If the column is not selected, append the original value to the winsorized row
                winsorized_row.append(val)
        # Append the winsorized row to the list of winsorized data
        winsorized_data.append(winsorized_row)

    return winsorized_data

