import os
import pandas as pd

# Configurations
DATASET_PATH = r"C:\Users\user\Downloads\archive\images\images"
EXCEL_PATH = r"C:\Users\user\Downloads\Data_Dictionary.xlsx"

# 1. Load data from the sheet
df = pd.read_excel(EXCEL_PATH, sheet_name='categories (values)', header=2)

df.columns = ['model_label_index', 'name_folder', 'display_name', 'suggested_bin']

df = df.dropna(subset=['model_label_index'])

# Convert the label index column explicitly to integers now that strings are filtered out
df['model_label_index'] = df['model_label_index'].astype(int)

dict_categories = df['name_folder'].tolist()
dict_mapping = {row['name_folder']: int(row['model_label_index']) for _, row in df.iterrows()}

# 2. Check physical folders on disk
if not os.path.exists(DATASET_PATH):
    print(f"Error: Cannot find raw dataset path at '{DATASET_PATH}'. Update the path in the script.")
else:
    disk_folders = sorted([f for f in os.listdir(DATASET_PATH) if os.path.isdir(os.path.join(DATASET_PATH, f))])
    
print("====== 1. VERIFYING FOLDER NAMES ======")
missing_on_disk = [c for c in dict_categories if c not in disk_folders]
extra_on_disk = [f for f in disk_folders if f not in dict_categories]

if not missing_on_disk and not extra_on_disk:
    print("[SUCCESS] The 30 category folder names match the dataset exactly!")
else:
    if missing_on_disk: 
        print(f"[WARNING] Missing from Disk (defined in Excel but not in folder): {missing_on_disk}")
    if extra_on_disk: 
        print(f"[WARNING] Extra on Disk (found in folder but missing from Excel): {extra_on_disk}")

print("\n====== 2. VERIFYING ML LABEL ORDER (ALPHABETICAL LOOKUP) ======")
mismatches = 0
for idx, folder_name in enumerate(disk_folders):
    expected_idx = dict_mapping.get(folder_name)
    if expected_idx is not None and expected_idx != idx:
        print(f"[ERROR] Label Order Mismatch: '{folder_name}' is index {idx} on disk, but Excel states it should be index {expected_idx}!")
        mismatches += 1
        
if mismatches == 0:
    print("[SUCCESS] The alphabetical dataset index order matches the `model_label_index` perfectly!")
else:
    print(f"[ERROR] Found {mismatches} framework alignment issues. Adjust the DB seeding script index fields before running.")