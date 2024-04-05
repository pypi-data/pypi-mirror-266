import chardet
import pandas as pd

def fillna_categorical_columns(df, columns):
    """
    Fill missing values in categorical columns with -1
    """
    for column in columns:
        df[column] = df[column].fillna(-1)
    return df

def fillna_date_columns(df, columns):
    """
    Fill missing values in date columns with 2999-12-31
    """
    for column in columns:
        df[column] = df[column].fillna('2999-12-31')
    return df

def check_encoding(file_path):
    """
    Check encoding of a file
    """
    with open(file_path, 'rb') as rawdata:
        result = chardet.detect(rawdata.read())
    return result['encoding']

def add_nan_row(df, dfKey):
    """
    Add rows with NaN values in all the columns
    """
    # add a row that simulates the scenario where all values are nan
    nan_col = {col:pd.NA for col in df.columns}
    nan_col[dfKey] = -1
    df.loc[len(df)] = nan_col
    return df

def generate_dim(data, filename):
    pd.DataFrame(data).to_csv(filename, index=False)

def check_encoding(file_path):
    """
    Check encoding of a file
    """
    with open(file_path, 'rb') as rawdata:
        result = chardet.detect(rawdata.read())
    return result['encoding']