import pandas as pd


def drop_null_values_from_selected_columns(input_data, selected_columns, column_names):
    """
    Drops null values from selected columns in a DataFrame.

    Parameters:
        input_data (list of lists): The input data as a list of lists.
        selected_columns (list): A list of column names from which null values will be dropped.
        column_names (list): A list of all column names in the DataFrame.

    Returns:
        list of lists: The output data with null values dropped from selected columns.
    """
    try:
        # Convert input data to a DataFrame
        df = pd.DataFrame(input_data, columns=column_names)
        
        # Convert selected column names to indices
        selected_column_indices = [df.columns.get_loc(col) for col in selected_columns]
        
        # Drop null values from selected columns
        df.dropna(subset=selected_columns, inplace=True)
        
        # Convert DataFrame back to a list of lists
        output_data = df.values.tolist()
        
        return output_data
    except Exception as e:
        # Handle any errors that might occur
        print(f"An error occurred: {str(e)}")
        return None





def fill_null_with_mean(data, column_names):
    # Convert input data to DataFrame
    df = pd.DataFrame(data, columns=column_names)
    
    # Iterate through each column
    for column_name in column_names:
        # Calculate mean of the specified column
        column_mean = df[column_name].mean()
        # Fill null values in the specified column with its mean
        df[column_name].fillna(column_mean, inplace=True)
    
    # Convert DataFrame back to list of lists
    filled_data = df.values.tolist()
    
    return filled_data


def fill_null_with_mode(data, column_names):
    # Convert input data to DataFrame
    df = pd.DataFrame(data, columns=column_names)
    
    # Iterate through each column
    for column_name in column_names:
        # Calculate mode of the specified column
        column_mode = df[column_name].mode()[0]  # Get the mode value; [0] because mode() returns a Series
        # Fill null values in the specified column with its mode
        df[column_name].fillna(column_mode, inplace=True)
    
    # Convert DataFrame back to list of lists
    filled_data = df.values.tolist()
    
    return filled_data

def fill_null_with_median(data, column_names):
    # Convert input data to DataFrame
    df = pd.DataFrame(data, columns=column_names)
    
    # Iterate through each column
    for column_name in column_names:
        # Calculate median of the specified column
        column_median = df[column_name].median()
        # Fill null values in the specified column with its median
        df[column_name].fillna(column_median, inplace=True)
    
    # Convert DataFrame back to list of lists
    filled_data = df.values.tolist()
    
    return filled_data



import pandas as pd





def drop_duplicates_all_columns(data):
    """
    Remove duplicate rows from a list of lists representing tabular data.
    :param data: List of lists representing the data
    :return: List of lists with duplicate rows removed
    """
    # Convert input data to DataFrame
    df = pd.DataFrame(data)
    
    # Drop duplicate rows
    df.drop_duplicates(inplace=True)
    
    # Convert DataFrame back to list of lists
    cleaned_data = df.values.tolist()
    
    return cleaned_data


def remove_duplicates_from_specific_columns(data, columns):
    """
    Remove duplicate values from specific columns of a list of lists.
    :param data: List of lists representing the data
    :param columns: List of column indices to remove duplicates from
    :return: List of lists with duplicates removed from specified columns
    """
    # Convert list of lists to DataFrame
    df = pd.DataFrame(data)
    
    # Convert column indices to column names
    column_names = df.columns[columns].tolist()
    
    # Remove duplicates from specified columns
    for column in column_names:
        if column in df.columns:
            df[column] = df[column].drop_duplicates()
        else:
            print(f"Column '{column}' not found in the DataFrame.")
    
    # Convert DataFrame back to list of lists
    cleaned_data = df.values.tolist()
    
    return cleaned_data


