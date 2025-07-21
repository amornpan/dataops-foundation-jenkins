#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple Test Script - รันจาก root directory
"""

def test_all():
    print("="*60)
    print("🧪 Simple ETL Test")
    print("="*60)
    
    # Test 1: Data file
    print("\n🔍 Testing data file...")
    try:
        import pandas as pd
        df = pd.read_csv('data/LoanStats_web_small.csv', low_memory=False)
        print(f"✅ Data loaded: {len(df):,} rows, {len(df.columns)} columns")
    except Exception as e:
        print(f"❌ Data test failed: {e}")
        return
    
    # Test 2: Database connection
    print("\n🔍 Testing database connection...")
    try:
        from sqlalchemy import create_engine, text
        engine = create_engine('mssql+pymssql://SA:Passw0rd123456@mssql.minddatatech.com/TestDB')
        with engine.connect() as connection:
            result = connection.execute(text('SELECT 1'))
            print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database test failed: {e}")
    
    # Test 3: ETL functions
    print("\n🔍 Testing ETL functions...")
    try:
        import etl_main
        result, types = etl_main.guess_column_types('data/LoanStats_web_small.csv')
        if result:
            print(f"✅ ETL functions working: {len(types)} columns analyzed")
        else:
            print(f"❌ ETL functions failed: {types}")
    except Exception as e:
        print(f"❌ ETL test failed: {e}")
    
    # Test 4: Run full ETL
    print("\n🔍 Running full ETL pipeline...")
    try:
        etl_main.main()
        print("✅ ETL pipeline completed successfully")
    except Exception as e:
        print(f"❌ ETL pipeline failed: {e}")
    
    print("\n" + "="*60)
    print("🎉 Testing completed!")
    print("="*60)

if __name__ == "__main__":
    test_all()
