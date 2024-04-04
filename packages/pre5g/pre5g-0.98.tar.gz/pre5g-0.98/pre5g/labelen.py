# def label_encoding_all(data):
#     """
#     Apply label encoding to all columns containing categorical values in the dataset.

#     Parameters:
#     data (list of lists): Input dataset.

#     Returns:
#     list of lists: Transformed dataset after label encoding.
#     """
#     df = pd.DataFrame(data)
#     categorical_cols = df.select_dtypes(include=['object', 'category']).columns
#     if not categorical_cols.empty:
#         for col in categorical_cols:
#             df[col] = df[col].astype('category').cat.codes
#         return df.values.tolist()
#     return data


from sklearn.preprocessing import LabelEncoder

def label_encoding_selected(data, columns):
    """
    Perform label encoding on selected columns while retaining numeric values.

    Parameters:
    data (DataFrame): The input DataFrame.
    columns (list): List of column names to label encode.

    Returns:
    DataFrame: The DataFrame with selected columns label encoded.
    """
    # Copy the original DataFrame
    encoded_data = data.copy()
    
    # Initialize LabelEncoder
    label_encoder = LabelEncoder()
    
    # Iterate through selected columns
    for column in columns:
        # Check if column exists and is categorical
        if column in data.columns and data[column].dtype == 'object':
            # Perform label encoding
            encoded_data[column] = label_encoder.fit_transform(data[column])
    
    return encoded_data

# Example usage:
# Suppose 'data' is your DataFrame and you want to label encode columns ['column1', 'column2']:
# encoded_data = label_encode_selected(data, ['column1', 'column2'])
