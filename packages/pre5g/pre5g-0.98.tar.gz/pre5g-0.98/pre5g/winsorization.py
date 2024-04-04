

# def winsorize_data(data, selected_columns, lower_pct=5, upper_pct=95):
#     """
#     Apply Winsorization to selected columns of the dataset.

#     Parameters:
#         data (list of lists): The input data where each inner list represents a row of data.
#         selected_columns (list of str): The names of columns to which Winsorization should be applied.
#         lower_pct (float): The lower percentile threshold (default is 5).
#         upper_pct (float): The upper percentile threshold (default is 95).

#     Returns:
#         list of lists: The data with Winsorization applied to selected columns.
#     """
#     # Create a copy of the data to avoid modifying the original data
#     winsorized_data = [row[:] for row in data]

#     # Iterate over each column
#     for col_idx, col_name in enumerate(data[0]):
#         if col_name in selected_columns:
#             # Extract values of the column
#             col_values = [row[col_idx] for row in winsorized_data[1:]]  # Skip the header

#             # Check if the column contains numeric data
#             if all(isinstance(val, (int, float)) for val in col_values):
#                 # Calculate percentile values
#                 lower_value = np.percentile(col_values, lower_pct)
#                 upper_value = np.percentile(col_values, upper_pct)
                
#                 # Print percentiles
#                 print(f"Lower percentile for column {col_name}: {lower_value}")
#                 print(f"Upper percentile for column {col_name}: {upper_value}")

#                 # Apply Winsorization
#                 for row_idx, value in enumerate(col_values):
#                     if value < lower_value:
#                         winsorized_data[row_idx + 1][col_idx] = lower_value
#                     elif value > upper_value:
#                         winsorized_data[row_idx + 1][col_idx] = upper_value
#             else:
#                 # If the column contains non-numeric data, retain the data as it is
#                 pass

#     return winsorized_data


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

