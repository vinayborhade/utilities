import pandas as pd
import random
from collections import defaultdict

# Try reading the file with ISO-8859-1 encoding to resolve the UnicodeDecodeError
df = pd.read_csv('D:/Projects/utilities/production_data_classfn.csv', encoding='ISO-8859-1') # use your csv file with classification column

# Get all Ultimate Parents
ultimate_parents = df[df['Classification'] == 'Ultimate parent']
# print(ultimate_parents)

processed_items = set()

# Iterate over each Ultimate Parent to build its hierarchy
for _, ultimate_parent in ultimate_parents.iterrows():
    # Extract the Item number and Number (relationship key) for the ultimate parent
    ultimate_parent_number = ultimate_parent['Number']
    ultimate_parent_item = ultimate_parent['Item number']
    ultimate_parent_name = ultimate_parent['Product description']

    # Skip if the child (intermediate or ultimate) is already processed
    if ultimate_parent_item in processed_items:
        continue
        
    # Mark the child as processed
    processed_items.add(ultimate_parent_item)

    # Step 2: Filter rows where NUMBER is the same as the Ultimate Parent's NUMBER and Reference is either Intermediate or Ultimate Child
    related_rows = df[(df['Number'] == ultimate_parent_number) & 
                    (df['Classification'].isin(['Intermediate parent', 'Ultimate child']))]
    
    related_rows_ultimate_child = related_rows[related_rows['Classification'].isin(['Ultimate child'])]

    # print(related_rows)

    related_rows_intermediate_parent = related_rows[related_rows['Classification'].isin(['Intermediate parent'])]
    if len(related_rows_intermediate_parent) >= 1:
        item = related_rows_intermediate_parent['Item number'].iloc[0]

        intermediate_rows = df[(df['Item number'] == item) & (df['Reference'].isin(['Production']))]

        numbers = intermediate_rows['Number']

        # print(numbers.to_list())

        child_rows = df[(df['Number'].isin(numbers.to_list())) & (df['Reference'].isin(['Production line']))]

        all_children = pd.concat([child_rows, related_rows_ultimate_child]) # this will merge all direct children and intermediate parent's children

        print('NUMBER:', ultimate_parent['Number'], '; Product: ', ultimate_parent_name,' - Children Count:', len(all_children)) 

        # Next steps
    # Group the rows by Product description and sum the qty and amounts
    # Order the rows in descending order by qty/amount to pick top 9 products and put rest in other category

