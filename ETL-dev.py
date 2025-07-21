#!/usr/bin/env python
# coding: utf-8

import re
import pandas as pd
from sqlalchemy import create_engine
import urllib
import warnings
warnings.filterwarnings('ignore')

### กำหนด data type ที่เหมาะสมกับ attribute values (Custom data types) ###

def guess_column_types(file_path, delimiter=',', has_headers=True):
    try:
        # Read the CSV file using the specified delimiter and header settings
        df = pd.read_csv(file_path, sep=delimiter,low_memory=False, header=0 if has_headers else None)

        # Initialize a dictionary to store column data types
        column_types = {}

        # Loop through columns and infer data types
        for column in df.columns:
            # sample_values = df[column].dropna().sample(min(5, len(df[column])), random_state=42)

            # Check for datetime format "YYYY-MM-DD HH:MM:SS"
            is_datetime = all(re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', str(value)) for value in df[column])

            # Check for date format "YYYY-MM-DD"
            is_date = all(re.match(r'\d{4}-\d{2}-\d{2}', str(value)) for value in df[column])

            # Assign data type based on format detection
            if is_datetime:
                inferred_type = 'datetime64'
            elif is_date:
                inferred_type = 'date'
            else:
                inferred_type = pd.api.types.infer_dtype(df[column], skipna=True)

            column_types[column] = inferred_type

        return (True, column_types)  # Return success and column types
    except pd.errors.ParserError as e:
        return (False, str(e))  # Return error message


def main():
    # Configuration
    file_path = 'data/LoanStats_web_small.csv'
    acceptableMax_null = 26
    
    # Database configuration - ปรับให้ใช้ 35.185.131.47
    server = '35.185.131.47'
    database = 'TestDB'
    username = 'SA'
    password = 'Passw0rd123456'
    
    print("=== ETL Pipeline Started ===")
    
    # Step 1: Guess column types
    print("Step 1: Analyzing column types...")
    result, column_types_or_error = guess_column_types(file_path)
    
    if not result:
        print(f"Error: {column_types_or_error}")
        return
    
    print(f"✅ Column types analyzed: {len(column_types_or_error)} columns")
    
    # Step 2: Load raw data
    print("Step 2: Loading raw data...")
    raw_df = pd.read_csv(file_path, low_memory=False)
    print(f"✅ Loaded {len(raw_df):,} rows, {len(raw_df.columns)} columns")
    
    # Step 3: Filter columns by missing data percentage
    print("Step 3: Filtering columns by missing data...")
    missing_percentage = raw_df.isnull().mean() * 100
    columns_to_keep = missing_percentage[missing_percentage <= 30].index.tolist()
    filteredCol_df = raw_df[columns_to_keep]
    print(f"✅ Kept {len(columns_to_keep)} columns (≤30% missing data)")
    
    # Step 4: Filter rows by acceptable null count
    print("Step 4: Filtering rows by null count...")
    selected_columns = [col for col in filteredCol_df.columns if filteredCol_df[col].isnull().sum() <= acceptableMax_null]
    df_selected = filteredCol_df[selected_columns]
    noNull_df = df_selected.dropna()
    print(f"✅ Selected {len(selected_columns)} columns, {len(noNull_df):,} clean rows")
    
    # Step 5: Data transformation
    print("Step 5: Transforming data...")
    df_prepared = noNull_df.copy()
    
    # Transform issue_d to datetime
    if 'issue_d' in df_prepared.columns:
        df_prepared['issue_d'] = pd.to_datetime(df_prepared['issue_d'], format='%b-%Y')
        print("✅ Converted issue_d to datetime")
    
    # Transform int_rate to float
    if 'int_rate' in df_prepared.columns and df_prepared['int_rate'].dtype == 'object':
        df_prepared['int_rate'] = df_prepared['int_rate'].str.rstrip('%').astype('float') / 100.0
        print("✅ Converted int_rate to float")
    
    # Step 6: Create dimension tables
    print("Step 6: Creating dimension tables...")
    
    # Home ownership dimension
    if 'home_ownership' in df_prepared.columns:
        home_ownership_dim = df_prepared[['home_ownership']].drop_duplicates().reset_index(drop=True)
        home_ownership_dim['home_ownership_id'] = home_ownership_dim.index
        print(f"✅ Home ownership dimension: {len(home_ownership_dim)} records")
    
    # Loan status dimension
    if 'loan_status' in df_prepared.columns:
        loan_status_dim = df_prepared[['loan_status']].drop_duplicates().reset_index(drop=True)
        loan_status_dim['loan_status_id'] = loan_status_dim.index
        print(f"✅ Loan status dimension: {len(loan_status_dim)} records")
    
    # Issue date dimension
    if 'issue_d' in df_prepared.columns:
        issue_d_dim = df_prepared[['issue_d']].drop_duplicates().reset_index(drop=True)
        issue_d_dim['month'] = issue_d_dim['issue_d'].dt.month
        issue_d_dim['year'] = issue_d_dim['issue_d'].dt.year
        issue_d_dim['issue_d_id'] = issue_d_dim.index
        print(f"✅ Issue date dimension: {len(issue_d_dim)} records")
    
    # Step 7: Create fact table
    print("Step 7: Creating fact table...")
    
    # Create mapping dictionaries
    home_ownership_map = home_ownership_dim.set_index('home_ownership')['home_ownership_id'].to_dict()
    loan_status_map = loan_status_dim.set_index('loan_status')['loan_status_id'].to_dict()
    issue_d_map = issue_d_dim.set_index('issue_d')['issue_d_id'].to_dict()
    
    # Create fact table
    loans_fact = df_prepared.copy()
    loans_fact['home_ownership_id'] = loans_fact['home_ownership'].map(home_ownership_map)
    loans_fact['loan_status_id'] = loans_fact['loan_status'].map(loan_status_map)
    loans_fact['issue_d_id'] = loans_fact['issue_d'].map(issue_d_map)
    
    # Select fact columns
    fact_columns = ['application_type', 'loan_amnt', 'funded_amnt', 'term', 'int_rate', 
                   'installment', 'home_ownership_id', 'loan_status_id', 'issue_d_id']
    available_columns = [col for col in fact_columns if col in loans_fact.columns]
    loans_fact = loans_fact[available_columns]
    
    print(f"✅ Fact table created: {len(loans_fact):,} records, {len(available_columns)} columns")
    
    # Step 8: Load to database
    print("Step 8: Loading to database...")
    
    try:
        # Create database engine
        engine = create_engine(f'mssql+pymssql://{username}:{password}@{server}/{database}')
        
        # Load dimension tables
        home_ownership_dim.to_sql('home_ownership_dim', con=engine, if_exists='replace', index=False)
        print("✅ home_ownership_dim loaded")
        
        loan_status_dim.to_sql('loan_status_dim', con=engine, if_exists='replace', index=False)
        print("✅ loan_status_dim loaded")
        
        issue_d_dim.to_sql('issue_d_dim', con=engine, if_exists='replace', index=False)
        print("✅ issue_d_dim loaded")
        
        # Load fact table
        loans_fact.to_sql('loans_fact', con=engine, if_exists='replace', index=False)
        print("✅ loans_fact loaded")
        
        print("=== ETL Pipeline Completed Successfully ===")
        
    except Exception as e:
        print(f"❌ Database loading failed: {str(e)}")
        return
    
    # Display summary
    print("\n📊 ETL Summary:")
    print(f"   Original data: {len(raw_df):,} rows, {len(raw_df.columns)} columns")
    print(f"   Clean data: {len(noNull_df):,} rows, {len(selected_columns)} columns")
    print(f"   Home ownership types: {len(home_ownership_dim)}")
    print(f"   Loan status types: {len(loan_status_dim)}")
    print(f"   Date range: {len(issue_d_dim)} unique dates")
    print(f"   Final fact table: {len(loans_fact):,} records")


if __name__ == "__main__":
    main()
