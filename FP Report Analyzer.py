# Forward Power Report Analyzer - Smart Comparison & Trend Detection

import pandas as pd
import os
from datetime import datetime

# --- Helper Functions ---
def extract_date_from_filename(filename):
    try:
        # Example: "Forward Power Problem Report(May 20).csv"
        date_str = filename.split("(")[1].replace(").csv", "").strip().replace(")", "")
        return datetime.strptime(date_str, "%b %d")
    except Exception as e:
        print(f"Failed to parse date from {filename}: {e}")
        return datetime.min

# --- Load and Sort Files by Date ---
folder_path = "."  # Replace with actual path
files = [f for f in os.listdir(folder_path) if f.endswith(".csv") and "Forward Power Problem Report" in f]
sorted_files = sorted(files, key=extract_date_from_filename, reverse=True)

if len(sorted_files) < 2:
    raise Exception("Not enough data files for comparison.")

newest_file = sorted_files[0]
previous_file = sorted_files[1]

print(f"📂 Comparing: {previous_file} ➡️ {newest_file}")

# --- Load Data ---
df_new = pd.read_csv(os.path.join(folder_path, newest_file))
df_old = pd.read_csv(os.path.join(folder_path, previous_file))

# --- Standardize Columns ---
df_new.columns = ['Site', 'FP', 'Issue']
df_old.columns = ['Site', 'FP', 'Issue']
df_new['Site'] = df_new['Site'].astype(str).str.strip()
df_old['Site'] = df_old['Site'].astype(str).str.strip()

# --- Merge Issues from Past ---
merged_df = pd.merge(df_new, df_old[['Site', 'Issue']], on='Site', how='left', suffixes=('', '_Prev'))
merged_df['Issue'] = merged_df['Issue'].combine_first(merged_df['Issue_Prev'])
merged_df.drop(columns=['Issue_Prev'], inplace=True)

# --- Identify Truly New Sites ---
new_sites_df = merged_df[~merged_df['Site'].isin(df_old['Site'])][['Site', 'Issue']]

# --- Save Outputs ---
merged_output_path = f"merged_sites_{datetime.now().strftime('%Y-%m-%d')}.csv"
new_sites_output_path = f"new_sites_only_{datetime.now().strftime('%Y-%m-%d')}.csv"

merged_df.to_csv(merged_output_path, index=False)
new_sites_df.to_csv(new_sites_output_path, index=False)

print(f"✅ Merged with carried Issues: {merged_output_path}")
print(f"🆕 New Sites: {new_sites_output_path}")
