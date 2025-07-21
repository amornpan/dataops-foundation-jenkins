#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Quick Test Script สำหรับทดสอบการทำงานของระบบ
"""

import os
import sys
import pandas as pd
from sqlalchemy import create_engine, text

def test_data_file():
    """ทดสอบการอ่านไฟล์ข้อมูล"""
    print("🔍 Testing data file...")
    
    data_file = 'data/LoanStats_web_small.csv'
    
    if not os.path.exists(data_file):
        print(f"❌ Data file not found: {data_file}")
        print("   Please copy the file to data/ folder")
        return False
    
    try:
        df = pd.read_csv(data_file, low_memory=False)
        print(f"✅ Data file loaded: {len(df):,} rows, {len(df.columns)} columns")
        
        # Check required columns
        required_cols = ['loan_amnt', 'funded_amnt', 'term', 'int_rate', 'installment',
                        'home_ownership', 'loan_status', 'issue_d', 'application_type']
        
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            print(f"⚠️  Missing required columns: {missing_cols}")
        else:
            print("✅ All required columns found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading data file: {str(e)}")
        return False

def test_database_connection():
    """ทดสอบการเชื่อมต่อฐานข้อมูล"""
    print("\n🔍 Testing database connection...")
    
    server = 'mssql.minddatatech.com'
    database = 'TestDB'
    username = 'SA'
    password = 'Passw0rd123456'
    
    try:
        engine = create_engine(f'mssql+pymssql://{username}:{password}@{server}/{database}')
        
        with engine.connect() as connection:
            result = connection.execute(text('SELECT 1 as test'))
            test_value = result.fetchone()[0]
            
            if test_value == 1:
                print("✅ Database connection successful")
                
                # Test table existence
                tables_check = connection.execute(text("""
                    SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES 
                    WHERE TABLE_NAME IN ('home_ownership_dim', 'loan_status_dim', 'issue_d_dim', 'loans_fact')
                """))
                table_count = tables_check.fetchone()[0]
                
                if table_count > 0:
                    print(f"✅ Found {table_count} existing star schema tables")
                else:
                    print("ℹ️  No star schema tables found (will be created during ETL)")
                
                return True
            else:
                print("❌ Database connection test failed")
                return False
                
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        print("   Please check:")
        print("   - Network connectivity to mssql.minddatatech.com")
        print("   - SQL Server is running")
        print("   - Credentials are correct")
        return False

def test_etl_pipeline():
    """ทดสอบการทำงานของ ETL pipeline"""
    print("\n🔍 Testing ETL pipeline...")
    
    try:
        # Add current directory to Python path
        import sys
        import os
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, current_dir)
        
        # Import และทดสอบ ETL functions
        import etl_main
        
        # Test column type detection
        result, column_types = etl_main.guess_column_types('data/LoanStats_web_small.csv')
        
        if result:
            print(f"✅ Column type detection working: {len(column_types)} columns analyzed")
        else:
            print(f"❌ Column type detection failed: {column_types}")
            return False
        
        # Test data loading
        df = pd.read_csv('data/LoanStats_web_small.csv', low_memory=False)
        print(f"✅ Data loading working: {len(df):,} rows loaded")
        
        return True
        
    except Exception as e:
        print(f"❌ ETL pipeline test failed: {str(e)}")
        return False

def test_unit_tests():
    """ทดสอบการทำงานของ unit tests"""
    print("\n🔍 Testing unit test framework...")
    
    try:
        # Import test modules
        sys.path.append('tests')
        import test_etl_pipeline
        
        # Test การโหลด test classes
        test_loader = test_etl_pipeline.unittest.TestLoader()
        test_suite = test_loader.loadTestsFromTestCase(test_etl_pipeline.TestDataLoading)
        
        print("✅ Unit test framework working")
        print(f"   Found {test_suite.countTestCases()} test cases in TestDataLoading")
        
        return True
        
    except Exception as e:
        print(f"❌ Unit test framework failed: {str(e)}")
        return False

def main():
    """รันการทดสอบทั้งหมด"""
    print("="*60)
    print("🧪 DataOps Foundation Jenkins - Quick Test")
    print("="*60)
    
    tests = [
        ("Data File", test_data_file),
        ("Database Connection", test_database_connection),
        ("ETL Pipeline", test_etl_pipeline),
        ("Unit Tests", test_unit_tests)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 Test Results Summary:")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready to use.")
        print("\nNext steps:")
        print("   1. Run ETL pipeline: python ETL-dev.py")
        print("   2. Run full unit tests: python tests\\test_etl_pipeline.py")
        print("   3. Setup Jenkins pipeline")
    else:
        print(f"\n⚠️  {total-passed} test(s) failed. Please fix issues before proceeding.")
        
        if not results[0][1]:  # Data file test failed
            print("\n💡 To fix data file issue:")
            print('   copy "C:\\Users\\Asus\\dataops-foundation\\LoanStats_web_small.csv" "data\\"')
        
        if not results[1][1]:  # Database test failed
            print("\n💡 To fix database issue:")
            print("   - Check network connection")
            print("   - Verify SQL Server is running")
            print("   - Confirm credentials are correct")

if __name__ == "__main__":
    main()
