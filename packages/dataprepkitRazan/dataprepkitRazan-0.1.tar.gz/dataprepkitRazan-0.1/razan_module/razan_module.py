import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder, LabelEncoder

def read_excel(file_path):
  return pd.read_csv(file_path)

def read_csv(file_path):
  return pd.read_csv(file_path)

def read_json(file_path):
  return pd.read_json(file_path)

def read_xml(file_path):
  return pd.read_xml(file_path)

def data_summary(data):

    print("Summary Statistics:")
    print(data.describe())

    print("\nMost Frequent Values:")
    for column in data.columns:
      #return most value repeated as series (could have two values with same count)
      #series (id : most value)
        most_frequent = data[column].mode()
      #access the first value of series 
                                                                #acesss series of value : count then take the max count
        print(f"{column}: {most_frequent.values[0]} (Frequency: {data[column].value_counts().max()})")
# Series containing the sum of missing values for each column.
    print("\nMissing Values:")
    print(data.isnull().sum())

    print("\nUnique Values:")
    for column in data.columns:
      #series (id : all values)
        unique_values = data[column].unique()
        print(f"{column}: {unique_values}")

    print("\nData Types:")
    print(data.dtypes)
#rows , columns
    print("\nData Shape:")
    print(data.shape)
#name , isnull , count , dtype
    print("\nData Information:")
    print(data.info())

    print("\nData Head:")
    print(data.head())

    print("\nData Tail:")
    print(data.tail())  
def handle_missing_values(data, strategy='drop', **kwargs):
# "keyword arguments" : dictionary 
    if strategy == 'drop':
        # Drop rows with any missing values
        cleaned_data = data.dropna()
        return cleaned_data
    elif strategy == 'impute':
      #fist row 
        # Impute missing values based on provided strategy
        imputed_data = impute_missing_values(data, **kwargs)
        return imputed_data
    else:
        raise ValueError("Invalid strategy. Choose either 'drop' or 'impute'.")


def impute_missing_values(data, method='mean'):
   # method (str): Options are 'mean', 'median', or 'mode'.

    numeric_columns = data.select_dtypes(include=['number']).columns
    if method == 'mean':
        return data.fillna(data[numeric_columns].mean())
    elif method == 'median':
        return data.fillna(data[numeric_columns].median())
    elif method == 'mode':
        return data.fillna(data[numeric_columns].mode().iloc[0])
    else:
        raise ValueError("Invalid imputation method. Choose either 'mean', 'median', or 'mode'.")
    

def one_hot_encode(data, categorical_cols):

    ohe = OneHotEncoder(sparse=False)
    encoded_data = ohe.fit_transform(data[categorical_cols])

    # Rename the columns
    #get values of clumns to make them column names
    column_names = ohe.get_feature_names_out(categorical_cols)
    encoded_df = pd.DataFrame(encoded_data, columns=column_names)

    # Extract non-categorical columns
    other_cols = data.drop(columns=categorical_cols)

    # Concatenate encoded categorical columns with other columns
    data_encoded = pd.concat([other_cols, encoded_df], axis=1)

    return data_encoded
    encoded_data = ohe.fit_transform(data[categorical_cols])

    # Rename the columns
    column_names = ohe.get_feature_names_out(categorical_cols)
    encoded_df = pd.DataFrame(encoded_data, columns=column_names)

    # Extract non-categorical columns
    other_cols = data.drop(columns=categorical_cols)

    # Concatenate encoded categorical columns with other columns
    data_encoded = pd.concat([other_cols, encoded_df], axis=1)

    return data_encoded

def label_encode(data, columns):
      for column in columns:
            encoder = LabelEncoder()
            data[column] = encoder.fit_transform(data[column])
      return data
  
