import pandas as pd


def rs_all(data):
    """
    Apply RobustScaler to all columns in the dataset, skipping string columns.

    Args:
    - data (list of lists): The data containing columns to scale.

    Returns:
    - scaled_data (list of lists): The scaled data.
    """
    scaled_data = []
    for column in data:
        # Check if the column contains only numeric values
        if all(isinstance(x, (int, float)) for x in column):
            median = np.median(column)
            quartile_1 = np.percentile(column, 25)
            quartile_3 = np.percentile(column, 75)
            iqr = quartile_3 - quartile_1
            scaled_column = [(x - median) / iqr for x in column]
        else:
            # If the column contains non-numeric values, keep the values unchanged
            scaled_column = column
        scaled_data.append(scaled_column)
    return scaled_data


def rs_selected_columns(data, selected_columns):
    """
    Apply Robust Scaler transformation to the selected columns in the data, skipping string columns.

    Args:
    - data (list of lists): The data containing columns to scale.
    - selected_columns (list of int): The indices of the columns to scale.

    Returns:
    - scaled_data (list of lists): The scaled data.
    """
    # Initialize lists to store median and IQR for each selected column
    column_medians = []
    column_iqrs = []

    # Calculate median and IQR for each selected column
    for col_index in selected_columns:
        # Extract column values, excluding non-numeric values
        column_values = [row[col_index] for row in data if isinstance(row[col_index], (int, float))]
        column_medians.append(np.median(column_values))
        q3, q1 = np.percentile(column_values, [75 ,25])
        column_iqrs.append(q3 - q1)

    # Apply Robust Scaling to each selected column
    scaled_data = []
    for row in data:
        scaled_row = []
        for i, val in enumerate(row):
            if i in selected_columns:
                # Check if the value is numeric before scaling
                if isinstance(val, (int, float)):
                    median = column_medians[selected_columns.index(i)]
                    iqr = column_iqrs[selected_columns.index(i)]
                    if iqr == 0:
                        scaled_val = 0  # Avoid division by zero
                    else:
                        scaled_val = (val - median) / iqr
                else:
                    scaled_val = val  # Preserve non-numeric values
                scaled_row.append(scaled_val)
            else:
                scaled_row.append(val)
        scaled_data.append(scaled_row)

    return scaled_data
