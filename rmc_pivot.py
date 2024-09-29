import os                     # OS Module in Python provides functions for interacting with Operating System
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))      # Add the parent directory to the sys.path
import pandas as pd           # Pandas is Fast and efficient for manipulating and analyzing data (Labelled Data).
import openpyxl               # Openpyxl Python library is use to read/write Excel 2010 xlsx/xlsm/xltx/xltm files.[XlsxWriter, xlrd can also be used]
import datetime
# from registry.input_output_registry import *
import logging
import xlsxwriter
import numpy as np
from collections import defaultdict
 
def load_data_from_excel(file_path):
    df = pd.read_excel(file_path)
    return df
 
def load_data_from_csv(file_path):
    df = pd.read_csv(file_path, encoding='ISO-8859-1')
    return df
 
def concat_dfs(dfs_lst):
    concat_df = pd.concat(dfs_lst, ignore_index=True)
    return concat_df  
 
def save_df_to_csv(filename, df):
    df.to_csv(filename, index=False)

def save_df_to_excel(filename, df):
    df.to_excel(filename)
 
def get_raw_data_from_folder(path, file_type='excel'):
 
    raw_data_lst = []
    for root, dir, files in os.walk(path):
        for file in files:
            file_path = path + file
            df = None
            if file_type == 'excel':
                df = load_data_from_excel(file_path)
 
            # elif file_type == 'csv':
            #     df = load_data_from_csv(file_path)
       
            raw_data_lst.append(df)
 
    return raw_data_lst


# Group the dataframe by 'Product description' and apply classification to each group once
def classify_product(group):
    unique_refs = group['Reference'].unique()
    if len(unique_refs) == 1:
        if 'Production' in unique_refs:
            return 'Ultimate parent'
        elif 'Production line' in unique_refs:
            return 'Ultimate child'
    elif 'Production' in unique_refs and 'Production line' in unique_refs:
        return 'Intermediate parent'
    else:
        return 'Unclassified'

# Function to assign Production and Production line based on 'Number' and 'Reference'
def assign_production_and_line(df):
    # Mapping Production Item numbers to Number
    production_map = df[df['Reference'] == 'Production'].groupby('Number')['Item number'].first()

    # Mapping Production line Item numbers to Number
    production_line_map = df[df['Reference'] == 'Production line'].groupby('Number')['Item number'].first()
    
    # Creating new columns 'Production' and 'Production line'
    df['Production'] = df['Number'].map(production_map)
    df['Production line'] = df['Number'].map(production_line_map)
    
    return df



def main():
    # raw_df = get_raw_data_from_folder(chen_rmc_registry.get('raw_data_folder'))
    # concat_df = concat_dfs(raw_df)
    # save_df_to_csv(chen_rmc_registry.get('test_combined'),concat_df)
    df_rmc = load_data_from_csv('D:/Projects/utilities/RMC Sales Merged with HSN.csv')
    # df_rmc = load_data_from_csv('D:/Projects/utilities/input.csv')

    # df = load_data_from_excel('D:/automation_prince/raw_data/RMC/Raw Data/PLANT 40/Plant 40 (01-01-2024 to 31-01-2024).xlsx')
    df_rmc = df_rmc.loc[df_rmc['Reference'].isin(['Production', 'Production line'])]
    print(len(df_rmc))

    # hsn_key_lst = df_rmc['HSN Key'].to_list()
    # hsn_key_lst = list(set(hsn_key_lst))

    # hsn_key_lst = ['39172390-PIPES-UPVC']

    # print(hsn_key_lst)

    # Group by 'Product description' and apply the classification function
    classification_mapping = df_rmc.groupby('Product description', group_keys=False).apply(
        lambda group: classify_product(group[['Reference']])
    )

    # Map the classification back to the original DataFrame
    df_rmc['Classification'] = df_rmc['Product description'].map(classification_mapping)

    # save_df_to_csv('D:/Projects/utilities/RMC Sales Classfn.csv', df_rmc)

    # Step 1: Group the data by 'Number' and 'Reference' to see corresponding Item numbers
    # Sort to make sure the data stays in order
    df_sorted = df_rmc.sort_values(by=['Number', 'Reference'])

    # Step 2: Pivot the data so that each 'Reference' value becomes a column
    pivot_df = df_sorted.pivot_table(index=['Item number', 'Product description', 'Classification'], columns=['Reference'], values=['Quantity'], aggfunc={'Quantity': np.sum}) #'Item number':lambda x: list(set(x)), 
    pivot_df = pivot_df.reset_index()
    print(pivot_df.head())

    save_df_to_excel('D:/Projects/utilities/pivot.xlsx', pivot_df)
   
if __name__ == "__main__":
    main()