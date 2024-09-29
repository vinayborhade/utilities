import pandas as pd
import json, codecs


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
def find_children(product_number, product_hierarchy):
    # Find all products with the same 'Number'
    
    number = df[df['Item number'] == product_number]['Number']
    number_lst = list(set(number))
    
    related_products = df[df['Number'].isin(number_lst)]
    related_products = related_products.drop_duplicates()
    

    
    # Initialize a list to hold the children of this parent
    children = []
        
    # Iterate over related products and classify them as Intermediate or Ultimate Children
    for _, product in related_products.iterrows():

        # Skip if the child (intermediate or ultimate) is already processed
        if product['Item number'] in processed_items:
            continue

        # print('Processing parent - ', ultimate_parent_item)
        # Mark the child as processed
        processed_items.add(product['Item number'])

        # print('number_lst count - ', len(number_lst), 'Related products count - ', len(related_products))

        if product['Classification'] == 'Intermediate parent' or product['Classification'] == 'Ultimate child':
            child_dict = {
                'Item number': product['Item number'],
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

# df = load_data_from_csv('D:/Projects/utilities/RMC Sales Merged with HSN.csv')
# df = load_data_from_csv('D:/Projects/utilities/10.csv')
df = load_data_from_csv('D:/Projects/utilities/input.csv')
print(len(df))
# Group by 'Product description' and apply the classification function
classification_mapping = df.groupby('Product description', group_keys=False).apply(
    lambda group: classify_product(group[['Reference']])
)

# Map the classification back to the original DataFrame
df['Classification'] = df['Product description'].map(classification_mapping)


# Initialize the dictionary to store the hierarchical relationships
product_hierarchy = {}

# Find all unique Ultimate Parents
ultimate_parents = df[df['Classification'] == 'Ultimate parent']
ultimate_parents = ultimate_parents[['Number','Reference','Item number','Product description', 'Classification']]
# ultimate_parents = ultimate_parents[['Number','Reference','Item number','Product description','HSN Key','Classification']]
ultimate_parents = ultimate_parents.drop_duplicates()
print(len(ultimate_parents))

# hsn_key_lst = ['39174000-FITTINGS-UPVC']
# hsn_parents = ultimate_parents[ultimate_parents['HSN Key'].isin(hsn_key_lst)]
# print(len(hsn_parents))

processed_items = set()

# product_hierarchy['IM100297'] = {
#         'Product description': 'Reducer [AQUAFIT]110mm X 90mm',
#         'Classification': 'Ultimate parent',
#         'Children': find_children('IM100297', product_hierarchy)
#     }

# with open('D:/Projects/utilities/IM100297.txt', 'wb') as f:
#     json.dump(product_hierarchy, codecs.getwriter('utf-8')(f), ensure_ascii=False, indent=4)

# Iterate over each Ultimate Parent and build the hierarchy
for _, parent in ultimate_parents.iterrows():
    # Initialize the structure for each ultimate parent
    print('generating dict for parent - ', parent['Product description'])
    product_hierarchy[parent['Item number']] = {
        'Product description': parent['Product description'],
        'Classification': parent['Classification'],
        'Children': find_children(parent['Item number'], product_hierarchy)
    }


 
with open('D:/Projects/utilities/10.txt', 'wb') as f:
    json.dump(product_hierarchy, codecs.getwriter('utf-8')(f), ensure_ascii=False, indent=4)
