"""
This is a module for matching exact columns in our PI2 data model. 
It provides functionality to identify and handle columns that match exactly across different datasets.
"""

import pandas as pd 

pi_data_model = pd.read_csv('business_definitions/pi20_data_model.csv')
pi_data_model = pi_data_model[['TABLE_NAME', 'COLUMN_NAME']]



source_data_sample = pd.read_csv('business_definitions/client_source_columns_sample.csv')

