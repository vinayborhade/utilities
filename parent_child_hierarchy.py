import pandas as pd
import json, codecs
import numpy as np


def load_data_from_csv(file_path):
    df = pd.read_csv(file_path, encoding='utf-8')
    return df

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

from collections import defaultdict

# Function to recursively find children of a given parent product
def find_children_item_number(product_number, product_hierarchy):
    related_products = df[df['Number'] == product_number]
    related_products = related_products.drop_duplicates()

    # Initialize a list to hold the children of this parent
    children_items = []

    # Iterate over related products and classify them as Intermediate or Ultimate Children
    for _, product in related_products.iterrows():

        if product['Classification'] == 'Ultimate child':
            children_items.append(product['Item number'])

        # Recursively find children for intermediate parents
        if product['Classification'] == 'Intermediate parent':
            # print('Finding childrn for - ', product['Item number'])
            find_children(product['Item number'], product_hierarchy)

    return children_items


# Function to recursively find children of a given parent product
def find_children(product_number, product_hierarchy):
    # Find all products with the same 'Number'
    
    number = df[df['Item number'] == product_number]['Number']
    number_lst = list(set(number))

    for num in number_lst:

    
        related_products = df[df['Number'] == num]
        related_products = related_products.drop_duplicates()
        
        
        # Initialize a list to hold the children of this parent
        children = []
        processed_items = set()
            
        # Iterate over related products and classify them as Intermediate or Ultimate Children
        for _, product in related_products.iterrows():

            # Skip if the child (intermediate or ultimate) is already processed
            if product['Number_Item_Key'] in processed_items:
                continue

            # print('Processing parent - ', ultimate_parent_item)
            # Mark the child as processed
            processed_items.add(product['Number_Item_Key'])

            # print('number_lst count - ', len(number_lst), 'Related products count - ', len(related_products))

            if product['Classification'] == 'Intermediate parent' or product['Classification'] == 'Ultimate child':
                child_dict = {
                    'Item number': product['Item number'],
                    'Number_Item_Key': product['Number_Item_Key'],
                    'Number' : product['Number'],
                    'Product description': product['Product description'],
                    'Classification': product['Classification'],
                    'Children': []
                }
                
                # Recursively find children for intermediate parents
                if product['Classification'] == 'Intermediate parent':
                    # print('Finding childrn for - ', product['Item number'])
                    child_dict['Children'] = find_children(product['Item number'], product_hierarchy)
                
                children.append(child_dict)
                # print('Appending child dict - ', child_dict)
        
        return children

df = load_data_from_csv('D:/Projects/utilities/RMC Sales Merged with HSN.csv')
# df = load_data_from_csv('D:/Projects/utilities//10.csv')
# df = load_data_from_csv('D:/Projects/utilities/input.csv')

df = df.loc[df['Reference'].isin(['Production', 'Production line'])]
print('Total Count - ', len(df))
# Group by 'Product description' and apply the classification function
classification_mapping = df.groupby('Product description', group_keys=False).apply(
    lambda group: classify_product(group[['Reference']])
)

# Map the classification back to the original DataFrame
df['Classification'] = df['Product description'].map(classification_mapping)
df['Number_Item_Key'] = df['Number'] + '_' + df['Item number']


# Initialize the dictionary to store the hierarchical relationships
product_hierarchy = {}

# Find all unique Ultimate Parents
ultimate_parents = df[df['Classification'] != 'Ultimate child']
# ultimate_parents = ultimate_parents[['Number','Reference','Item number','Product description', 'Classification']]
ultimate_parents = ultimate_parents[['Number','Reference','Item number','Product description','HSN Key','Classification']]
ultimate_parents = ultimate_parents.drop_duplicates()
print('Ultimate and Intermediate Parent Count ', len(ultimate_parents))

hsn_key_lst = ['39174000-FITTINGS-UPVC']
hsn_parents = ultimate_parents[ultimate_parents['HSN Key'].isin(hsn_key_lst)]
print('HSN Matched Parent Count - ', len(hsn_parents))

def get_related_numbers(hsn_parents, item_number, reference, classification):
    item_number_parents = hsn_parents[(hsn_parents['Item number'].isin(item_number)) & (hsn_parents['Reference'].isin(reference)) & (hsn_parents['Classification'].isin(classification))]
    # print('Item Number -', item_number, '; related parents count- ', len(item_number_parents))

    related_number_parents_lst = list(set(item_number_parents['Number']))
    
    return related_number_parents_lst

# ['PPFL-043339', 'PPFL-056707', 'PPFL-044654', 'PPFL-024949', 'PPFL-065396', 'PPFL-037705', 'PPFL-029670', 'PPFL-085300', 'PPFL-000222', 'PPFL-068532', 'PPFL-081883', 'PPFL-049585', 'PPFL-058185', 'PPFL-016838', 'PPFL-054763', 'PPFL-025716', 'PPFL-078294']

def get_related_item_numbers(ultimate_parents, number, reference, classification):
    item_number_parents = ultimate_parents[(ultimate_parents['Number'].isin(number)) & (ultimate_parents['Reference'].isin(reference)) & (ultimate_parents['Classification'].isin(classification))]
    # print('Number -', number, '; related rows count- ', len(item_number_parents))

    related_item_number_parents_lst = list(set(item_number_parents['Item number']))
    
    return related_item_number_parents_lst

# 1. List of Number column values, related to the top level item number to be retrieved.
# Top level Item numbers that have associated HSN key from Sales data to be searched in hsn_parents dataframe

# item_lst = ['SIM100297', 'SIM103350', 'SIM100300']

# hsn_parents_item_lst = hsn_parents['Item number']
hsn_parents_item_lst = ['SIM100297']
print(hsn_parents_item_lst)

top_parent_item_number_lst = hsn_parents_item_lst # 
print('Top level parents with HSN Count- ', len(top_parent_item_number_lst))

top_parents_number_lst = get_related_numbers(hsn_parents, top_parent_item_number_lst, ['Production'], ['Ultimate parent', 'Intermediate parent'])
# print(top_parents_number_lst)
print('Top level parents Number Count- ', len(top_parents_number_lst))

# 2. List of Item Number column values, related to the number values found in step 1 to be retrieved 
# Second Level and onwards Numbers and Item Numbers to be searched in ultimate_parents dataframe as hsn_parents dataframe has only top level data data

#2.a. Get intermediate parents
intermeidate_parent_item_number_lst = get_related_item_numbers(ultimate_parents, top_parents_number_lst, ['Production line'], ['Intermediate parent'])
print('Second level intermediate parent Item Number - ', sorted(intermeidate_parent_item_number_lst))

#2.a. Get children
children_item_number_lst = get_related_item_numbers(df, intermeidate_parent_item_number_lst, ['Production line'], ['Ultimate child'])
print('Second level children Item Number - ', sorted(children_item_number_lst))

# 3. Find List of Number column values, related to the item number found in earlier step 2.
related_number_intermediate_parents_lst = get_related_numbers(ultimate_parents, intermeidate_parent_item_number_lst, ['Production'], ['Intermediate parent'])
print('Second level parents Item Number Count- ', len(related_number_intermediate_parents_lst))# print(related_number_parents_lst)

#3.a. Get intermediate parents
related_item_number_lst = get_related_item_numbers(ultimate_parents, related_number_intermediate_parents_lst, ['Production line'], ['Intermediate parent'])
print('Third level Intermediate parent Item Number - ', sorted(related_item_number_lst))

#3.b. Get children
related_children_item_number_lst = get_related_item_numbers(df, related_number_intermediate_parents_lst, ['Production line'], ['Ultimate child'])
print('Third level Children Item Number - ', sorted(related_children_item_number_lst))


df_sorted = df.sort_values(by=['Number', 'Reference'])

df_sorted = df_sorted[(df_sorted['Item number'].isin(related_children_item_number_lst)) & (df_sorted['Number'].isin(related_number_intermediate_parents_lst))]
print('df count - ', len(df_sorted))

pivot_df = df_sorted.pivot_table(index=['Number', 'Item number', 'Product description', 'Classification', 'Reference'], values=['Quantity', 'Cost amount'], aggfunc={'Quantity': np.sum, 'Cost amount': np.sum}) #'Item number':lambda x: list(set(x)), 
pivot_df = pivot_df.reset_index()
print(pivot_df.head())

def save_df_to_excel(filename, df):
    df.to_excel(filename)

save_df_to_excel('D:/Projects/utilities/pivot.xlsx', pivot_df)

# product_hierarchy['IM100297'] = {
#         'Number': 'PPFL-000221',
#         'Number_Item_Key': 'PPFL-000221_IM100297',
#         'Product description': 'Reducer [AQUAFIT]110mm X 90mm',
#         'Classification': 'Ultimate parent',
#         'Children': find_children('IM100297', product_hierarchy)
#     }

# with open('D:/Projects/utilities//IM100297.txt', 'wb') as f:
#     json.dump(product_hierarchy, codecs.getwriter('utf-8')(f), ensure_ascii=False, indent=4)

# Iterate over each Ultimate Parent and build the hierarchy
# for _, parent in ultimate_parents.iterrows():
#     # Initialize the structure for each ultimate parent
#     print('generating dict for parent - ', parent['Product description'])
#     product_hierarchy[parent['Item number']] = {
        #   'Number_Item_Key': product['Number_Item_Key'],
#         'Product description': parent['Product description'],
#         'Classification': parent['Classification'],
#         'Children': find_children(parent['Item number'], product_hierarchy)
#     }


 
# with open('D:/Projects/utilities/10.txt', 'wb') as f:
#     json.dump(product_hierarchy, codecs.getwriter('utf-8')(f), ensure_ascii=False, indent=4)
