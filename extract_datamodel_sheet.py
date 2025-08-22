#!/usr/bin/env python3
"""
Extract the Data Model sheet from the Excel crosswalk template
"""

import pandas as pd
import os
import sys

def extract_datamodel_sheet():
    """Extract and analyze the Data Model sheet from Excel"""
    
    # Look for the Excel file
    excel_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.xlsx') and 'crosswalk' in file.lower():
                excel_files.append(os.path.join(root, file))
    
    if not excel_files:
        print("❌ No Excel crosswalk file found")
        return
    
    excel_file = excel_files[0]
    print(f"📁 Found Excel file: {excel_file}")
    
    try:
        # Load the Excel file and check sheet names
        excel_file_obj = pd.ExcelFile(excel_file)
        sheet_names = excel_file_obj.sheet_names
        print(f"📊 Available sheets: {', '.join(sheet_names)}")
        
        # Look for Data Model sheet
        data_model_sheet = None
        for sheet in sheet_names:
            if 'data' in sheet.lower() and 'model' in sheet.lower():
                data_model_sheet = sheet
                break
        
        if not data_model_sheet:
            print("❌ No 'Data Model' sheet found")
            print(f"Available sheets: {sheet_names}")
            return
        
        print(f"✅ Found Data Model sheet: '{data_model_sheet}'")
        
        # Read the data model sheet
        df = pd.read_excel(excel_file, sheet_name=data_model_sheet)
        print(f"📋 Data Model sheet has {len(df)} rows and {len(df.columns)} columns")
        
        # Display column names
        print(f"📝 Columns: {list(df.columns)}")
        
        # Display first few rows
        print(f"\n📊 First 10 rows of Data Model:")
        print(df.head(10).to_string())
        
        # Save to CSV for analysis
        output_file = "data_model_from_excel.csv"
        df.to_csv(output_file, index=False)
        print(f"\n💾 Saved data model to: {output_file}")
        
        # Analyze the structure
        print(f"\n🔍 Data Model Analysis:")
        print(f"Total fields: {len(df)}")
        
        # Check for common columns
        common_cols = ['column_name', 'table_name', 'data_type', 'description', 'schema']
        for col in common_cols:
            matches = [c for c in df.columns if col.lower() in c.lower()]
            if matches:
                print(f"  {col}: Found column '{matches[0]}'")
        
        # Show unique values for key columns
        for col in df.columns[:5]:  # First 5 columns
            unique_vals = df[col].dropna().unique()
            if len(unique_vals) <= 20:  # Only show if reasonable number
                print(f"  {col} values: {list(unique_vals)[:10]}")  # First 10 values
            else:
                print(f"  {col}: {len(unique_vals)} unique values")
        
        return df
        
    except Exception as e:
        print(f"❌ Error reading Excel file: {e}")
        return None

if __name__ == "__main__":
    extract_datamodel_sheet()