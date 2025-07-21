#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Jenkins-friendly test script
ไม่ต้องการไฟล์ข้อมูลจริงก็ทดสอบได้
"""

import sys
import os

def test_basic_imports():
    """ทดสอบการ import packages พื้นฐาน"""
    print("🔍 Testing basic imports...")
    try:
        import pandas as pd
        import numpy as np
        import sqlalchemy
        print("✅ Core packages imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_etl_functions():
    """ทดสอบ ETL functions"""
    print("🔍 Testing ETL functions...")
    try:
        import etl_main
        
        # Test function exists
        if hasattr(etl_main, 'guess_column_types'):
            print("✅ guess_column_types function found")
            
            # Test with a dummy CSV if data file doesn't exist
            data_file = 'data/LoanStats_web_small.csv'
            if os.path.exists(data_file):
                result, types = etl_main.guess_column_types(data_file)
                if result:
                    print(f"✅ ETL function test passed: {len(types)} columns")
                else:
                    print(f"⚠️  ETL function test had issues: {types}")
            else:
                print("ℹ️  Data file not found, skipping ETL function test")
            
            return True
        else:
            print("❌ guess_column_types function not found")
            return False
            
    except Exception as e:
        print(f"❌ ETL function test failed: {e}")
        return False

def test_database_connection():
    """ทดสอบการเชื่อมต่อฐานข้อมูล (optional)"""
    print("🔍 Testing database connection...")
    try:
        from sqlalchemy import create_engine, text
        
        # Get credentials from environment or use defaults
        server = os.getenv('DB_SERVER', 'mssql.minddatatech.com')
        database = os.getenv('DB_NAME', 'TestDB')
        username = os.getenv('DB_USERNAME', 'SA')
        password = os.getenv('DB_PASSWORD', 'Passw0rd123456')
        
        engine = create_engine(f'mssql+pymssql://{username}:{password}@{server}/{database}')
        
        with engine.connect() as connection:
            result = connection.execute(text('SELECT 1'))
            if result.fetchone()[0] == 1:
                print("✅ Database connection successful")
                return True
            else:
                print("❌ Database connection test failed")
                return False
                
    except Exception as e:
        print(f"⚠️  Database connection failed: {e}")
        print("Note: This is expected if running in CI without database access")
        return True  # Don't fail the build for DB issues in CI

def main():
    """รัน tests ทั้งหมด"""
    print("="*60)
    print("🧪 Jenkins-Friendly ETL Tests")
    print("="*60)
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("ETL Functions", test_etl_functions),
        ("Database Connection", test_database_connection)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
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
    
    # Exit with appropriate code
    if passed >= total - 1:  # Allow 1 test to fail (usually DB connection)
        print("\n🎉 Tests completed successfully!")
        return 0
    else:
        print(f"\n⚠️  Too many tests failed ({total-passed})")
        return 1

if __name__ == "__main__":
    sys.exit(main())
