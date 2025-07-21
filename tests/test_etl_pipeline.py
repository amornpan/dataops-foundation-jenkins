#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ETL Unit Testing Framework using Real Data from data/LoanStats_web_small.csv
ใช้ข้อมูลจริงจากไฟล์ CSV สำหรับการทดสอบแทนการสร้างข้อมูลจำลอง
"""

import unittest
import pandas as pd
import numpy as np
import os
import sys
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine, text
import warnings
warnings.filterwarnings('ignore')

class TestDataLoading(unittest.TestCase):
    """Test Suite สำหรับการโหลดและตรวจสอบข้อมูลต้นฉบับ"""
    
    @classmethod
    def setUpClass(cls):
        """เตรียมข้อมูลจาก CSV file"""
        cls.csv_file = 'data/LoanStats_web_small.csv'
        
        # ตรวจสอบว่าไฟล์มีอยู่จริง
        if not os.path.exists(cls.csv_file):
            raise FileNotFoundError(f"ไม่พบไฟล์ {cls.csv_file}")
    
    def test_csv_file_exists(self):
        """ทดสอบว่าไฟล์ CSV มีอยู่จริง"""
        self.assertTrue(os.path.exists(self.csv_file), f"ไฟล์ {self.csv_file} ต้องมีอยู่")
        print(f"✅ ไฟล์ {self.csv_file} พบแล้ว")
    
    def test_csv_file_readable(self):
        """ทดสอบว่าไฟล์ CSV อ่านได้"""
        try:
            df = pd.read_csv(self.csv_file, low_memory=False)
            self.assertGreater(len(df), 0, "ไฟล์ CSV ต้องมีข้อมูล")
            self.assertGreater(len(df.columns), 0, "ไฟล์ CSV ต้องมีคอลัมน์")
            print(f"✅ อ่านไฟล์สำเร็จ: {len(df):,} แถว, {len(df.columns)} คอลัมน์")
        except Exception as e:
            self.fail(f"ไม่สามารถอ่านไฟล์ CSV ได้: {str(e)}")
    
    def test_required_columns_exist(self):
        """ทดสอบว่าคอลัมน์ที่จำเป็นมีอยู่ใน CSV"""
        df = pd.read_csv(self.csv_file, low_memory=False)
        
        required_columns = [
            'loan_amnt', 'funded_amnt', 'term', 'int_rate', 'installment',
            'home_ownership', 'loan_status', 'issue_d', 'application_type'
        ]
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        self.assertEqual(len(missing_columns), 0, 
                        f"คอลัมน์ที่จำเป็นไม่พบ: {missing_columns}")
        print(f"✅ คอลัมน์ที่จำเป็นครบถ้วน: {required_columns}")


class TestDataQuality(unittest.TestCase):
    """Test Suite สำหรับ Data Quality Checks ใช้ข้อมูลจริง"""
    
    @classmethod
    def setUpClass(cls):
        """โหลดข้อมูลจริงจาก CSV"""
        cls.csv_file = 'data/LoanStats_web_small.csv'
        cls.raw_df = pd.read_csv(cls.csv_file, low_memory=False)
        print(f"โหลดข้อมูลต้นฉบับ: {len(cls.raw_df):,} แถว")
    
    def test_data_completeness(self):
        """ทดสอบความครบถ้วนของข้อมูล"""
        # คำนวณ missing percentage สำหรับแต่ละคอลัมน์
        missing_percentage = self.raw_df.isnull().mean() * 100
        
        # แสดงสถิติ missing data
        print("Missing data percentage by column:")
        for col, pct in missing_percentage.head(10).items():
            print(f"  {col}: {pct:.1f}%")
        
        # ทดสอบว่ามีคอลัมน์ที่มีข้อมูลเพียงพอสำหรับการวิเคราะห์
        usable_columns = missing_percentage[missing_percentage <= 30].index.tolist()
        self.assertGreater(len(usable_columns), 5, 
                          "ต้องมีคอลัมน์ที่ใช้งานได้อย่างน้อย 5 คอลัมน์")
        print(f"✅ คอลัมน์ที่ใช้งานได้ (≤30% missing): {len(usable_columns)} คอลัมน์")
    
    def test_loan_amount_validity(self):
        """ทดสอบความถูกต้องของ loan amount"""
        if 'loan_amnt' not in self.raw_df.columns:
            self.skipTest("คอลัมน์ loan_amnt ไม่พบ")
        
        loan_amnt = self.raw_df['loan_amnt'].dropna()
        
        # ทดสอบว่ามี loan amount ที่เป็นค่าบวก
        positive_loans = loan_amnt[loan_amnt > 0]
        self.assertGreater(len(positive_loans), 0, "ต้องมี loan amount ที่เป็นค่าบวก")
        
        # ทดสอบว่าค่าอยู่ในช่วงที่สมเหตุสมผล
        reasonable_loans = loan_amnt[(loan_amnt >= 1000) & (loan_amnt <= 100000)]
        reasonable_percentage = len(reasonable_loans) / len(loan_amnt) * 100
        
        print(f"Loan amount statistics:")
        print(f"  Valid loans: {len(positive_loans):,}")
        print(f"  Reasonable range (1K-100K): {reasonable_percentage:.1f}%")
        print(f"  Min: ${loan_amnt.min():,.2f}")
        print(f"  Max: ${loan_amnt.max():,.2f}")
        print(f"  Average: ${loan_amnt.mean():,.2f}")
        
        self.assertGreater(reasonable_percentage, 50, 
                          "อย่างน้อย 50% ของ loan amount ต้องอยู่ในช่วงที่สมเหตุสมผล")
        print("✅ Loan amount ผ่านการตรวจสอบ")


class TestETLPipeline(unittest.TestCase):
    """Test Suite สำหรับการทดสอบ ETL Pipeline แบบครบวงจร"""
    
    @classmethod
    def setUpClass(cls):
        """เตรียมข้อมูลและรัน ETL pipeline"""
        cls.csv_file = 'data/LoanStats_web_small.csv'
        
        if not os.path.exists(cls.csv_file):
            raise FileNotFoundError(f"ไม่พบไฟล์ {cls.csv_file}")
        
        # รัน ETL pipeline
        cls.run_etl_pipeline()
    
    @classmethod
    def run_etl_pipeline(cls):
        """รัน ETL pipeline เหมือนใน ETL-dev.py"""
        # Load raw data
        cls.raw_df = pd.read_csv(cls.csv_file, low_memory=False)
        
        # Filter columns by missing data
        missing_percentage = cls.raw_df.isnull().mean() * 100
        columns_to_keep = missing_percentage[missing_percentage <= 30].index.tolist()
        filtered_col_df = cls.raw_df[columns_to_keep]
        
        # Filter rows by null count
        acceptable_max_null = 26
        selected_columns = [col for col in filtered_col_df.columns 
                          if filtered_col_df[col].isnull().sum() <= acceptable_max_null]
        df_selected = filtered_col_df[selected_columns]
        cls.no_null_df = df_selected.dropna()
        
        # Transform data
        cls.df_prepared = cls.no_null_df.copy()
        
        if 'issue_d' in cls.df_prepared.columns:
            cls.df_prepared['issue_d'] = pd.to_datetime(cls.df_prepared['issue_d'], format='%b-%Y')
        
        if 'int_rate' in cls.df_prepared.columns and cls.df_prepared['int_rate'].dtype == 'object':
            cls.df_prepared['int_rate'] = cls.df_prepared['int_rate'].str.rstrip('%').astype('float') / 100.0
        
        # Create dimension tables
        if 'home_ownership' in cls.df_prepared.columns:
            cls.home_ownership_dim = cls.df_prepared[['home_ownership']].drop_duplicates().reset_index(drop=True)
            cls.home_ownership_dim['home_ownership_id'] = cls.home_ownership_dim.index
        
        if 'loan_status' in cls.df_prepared.columns:
            cls.loan_status_dim = cls.df_prepared[['loan_status']].drop_duplicates().reset_index(drop=True)
            cls.loan_status_dim['loan_status_id'] = cls.loan_status_dim.index
        
        if 'issue_d' in cls.df_prepared.columns:
            cls.issue_d_dim = cls.df_prepared[['issue_d']].drop_duplicates().reset_index(drop=True)
            cls.issue_d_dim['month'] = cls.issue_d_dim['issue_d'].dt.month
            cls.issue_d_dim['year'] = cls.issue_d_dim['issue_d'].dt.year
            cls.issue_d_dim['issue_d_id'] = cls.issue_d_dim.index
        
        # Create fact table
        home_ownership_map = cls.home_ownership_dim.set_index('home_ownership')['home_ownership_id'].to_dict()
        loan_status_map = cls.loan_status_dim.set_index('loan_status')['loan_status_id'].to_dict()
        issue_d_map = cls.issue_d_dim.set_index('issue_d')['issue_d_id'].to_dict()
        
        cls.loans_fact = cls.df_prepared.copy()
        cls.loans_fact['home_ownership_id'] = cls.loans_fact['home_ownership'].map(home_ownership_map)
        cls.loans_fact['loan_status_id'] = cls.loans_fact['loan_status'].map(loan_status_map)
        cls.loans_fact['issue_d_id'] = cls.loans_fact['issue_d'].map(issue_d_map)
        
        # Select fact columns
        fact_columns = ['application_type', 'loan_amnt', 'funded_amnt', 'term', 'int_rate', 
                       'installment', 'home_ownership_id', 'loan_status_id', 'issue_d_id']
        available_columns = [col for col in fact_columns if col in cls.loans_fact.columns]
        cls.loans_fact = cls.loans_fact[available_columns]
    
    def test_data_filtering_effectiveness(self):
        """ทดสอบประสิทธิภาพของการกรองข้อมูล"""
        original_rows = len(self.raw_df)
        clean_rows = len(self.no_null_df)
        
        # ข้อมูลที่เหลือต้องไม่น้อยกว่า 10% ของต้นฉบับ
        retention_rate = clean_rows / original_rows * 100
        self.assertGreaterEqual(retention_rate, 10,
                              "ต้องเก็บข้อมูลไว้อย่างน้อย 10% ของต้นฉบับ")
        
        print(f"✅ Data filtering: {retention_rate:.1f}% retention ({clean_rows:,}/{original_rows:,} rows)")
    
    def test_dimension_tables_creation(self):
        """ทดสอบการสร้าง dimension tables"""
        # Test home ownership dimension
        if hasattr(self, 'home_ownership_dim'):
            unique_home = self.df_prepared['home_ownership'].nunique()
            self.assertEqual(len(self.home_ownership_dim), unique_home,
                           "Home ownership dimension ต้องมีจำนวนเท่ากับ unique values")
            print(f"✅ Home ownership dimension: {len(self.home_ownership_dim)} records")
        
        # Test loan status dimension
        if hasattr(self, 'loan_status_dim'):
            unique_status = self.df_prepared['loan_status'].nunique()
            self.assertEqual(len(self.loan_status_dim), unique_status,
                           "Loan status dimension ต้องมีจำนวนเท่ากับ unique values")
            print(f"✅ Loan status dimension: {len(self.loan_status_dim)} records")
        
        # Test issue date dimension
        if hasattr(self, 'issue_d_dim'):
            unique_dates = self.df_prepared['issue_d'].nunique()
            self.assertEqual(len(self.issue_d_dim), unique_dates,
                           "Issue date dimension ต้องมีจำนวนเท่ากับ unique dates")
            print(f"✅ Issue date dimension: {len(self.issue_d_dim)} records")
    
    def test_fact_table_integrity(self):
        """ทดสอบความสมบูรณ์ของ fact table"""
        # ทดสอบจำนวนแถว
        self.assertEqual(len(self.loans_fact), len(self.df_prepared),
                        "Fact table ต้องมีจำนวนแถวเท่ากับข้อมูลที่เตรียมแล้ว")
        
        # ทดสอบ foreign key mapping
        if 'home_ownership_id' in self.loans_fact.columns:
            null_home_ids = self.loans_fact['home_ownership_id'].isnull().sum()
            self.assertEqual(null_home_ids, 0, "home_ownership_id mapping ต้องสำเร็จทั้งหมด")
        
        if 'loan_status_id' in self.loans_fact.columns:
            null_status_ids = self.loans_fact['loan_status_id'].isnull().sum()
            self.assertEqual(null_status_ids, 0, "loan_status_id mapping ต้องสำเร็จทั้งหมด")
        
        if 'issue_d_id' in self.loans_fact.columns:
            null_date_ids = self.loans_fact['issue_d_id'].isnull().sum()
            self.assertEqual(null_date_ids, 0, "issue_d_id mapping ต้องสำเร็จทั้งหมด")
        
        print(f"✅ Fact table integrity: {len(self.loans_fact):,} records")
    
    def test_business_rules(self):
        """ทดสอบ business rules"""
        # Test loan amount rules
        if 'loan_amnt' in self.loans_fact.columns:
            negative_loans = self.loans_fact[self.loans_fact['loan_amnt'] <= 0]
            self.assertEqual(len(negative_loans), 0, "ไม่ควรมี loan amount ≤ 0")
        
        # Test funded amount rules
        if 'loan_amnt' in self.loans_fact.columns and 'funded_amnt' in self.loans_fact.columns:
            overfunded = self.loans_fact[self.loans_fact['funded_amnt'] > self.loans_fact['loan_amnt']]
            self.assertEqual(len(overfunded), 0, "ไม่ควรมี funded amount > loan amount")
        
        # Test interest rate rules
        if 'int_rate' in self.loans_fact.columns:
            invalid_rates = self.loans_fact[(self.loans_fact['int_rate'] < 0) | (self.loans_fact['int_rate'] > 1)]
            self.assertEqual(len(invalid_rates), 0, "Interest rate ต้องอยู่ในช่วง 0-1")
        
        print("✅ Business rules validated")


class ETLTestRunner:
    """Class สำหรับรัน ETL tests แบบครบถ้วนกับข้อมูลจริง"""
    
    @staticmethod
    def run_all_tests():
        """รัน tests ทั้งหมดกับข้อมูลจาก data/LoanStats_web_small.csv"""
        print("="*80)
        print("🔍 เริ่มต้นการทดสอบ ETL Pipeline กับข้อมูลจริงจาก data/LoanStats_web_small.csv")
        print("="*80)
        
        # ตรวจสอบไฟล์ก่อนเริ่มทดสอบ
        if not os.path.exists('data/LoanStats_web_small.csv'):
            print("❌ ไม่พบไฟล์ data/LoanStats_web_small.csv")
            print("   กรุณาวางไฟล์ในโฟลเดอร์ data/")
            return False
        
        test_classes = [
            TestDataLoading,
            TestDataQuality,
            TestETLPipeline
        ]
        
        total_tests = 0
        total_failures = 0
        total_errors = 0
        
        for test_class in test_classes:
            print(f"\n📋 รันการทดสอบ: {test_class.__name__}")
            print("-" * 60)
            
            try:
                suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
                runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
                result = runner.run(suite)
                
                total_tests += result.testsRun
                total_failures += len(result.failures)
                total_errors += len(result.errors)
                
                if result.failures:
                    print(f"❌ ล้มเหลว: {len(result.failures)} test(s)")
                
                if result.errors:
                    print(f"⚠️ ข้อผิดพลาด: {len(result.errors)} test(s)")
                
            except Exception as e:
                print(f"❌ ข้อผิดพลาดในการรัน {test_class.__name__}: {str(e)}")
                total_errors += 1
        
        print(f"\n📊 สรุปผลการทดสอบทั้งหมด:")
        print("=" * 50)
        print(f"   - ทดสอบทั้งหมด: {total_tests}")
        print(f"   - ผ่าน: {total_tests - total_failures - total_errors}")
        print(f"   - ล้มเหลว: {total_failures}")
        print(f"   - ข้อผิดพลาด: {total_errors}")
        
        success_rate = ((total_tests - total_failures - total_errors) / total_tests * 100) if total_tests > 0 else 0
        print(f"   - อัตราความสำเร็จ: {success_rate:.1f}%")
        
        print("\n" + "="*80)
        
        return total_failures == 0 and total_errors == 0


if __name__ == "__main__":
    # รัน tests กับข้อมูลจริง
    runner = ETLTestRunner()
    success = runner.run_all_tests()
    
    if success:
        print("🎉 การทดสอบ ETL กับข้อมูลจริงสำเร็จทั้งหมด!")
        sys.exit(0)
    else:
        print("❌ พบปัญหาในการทดสอบ ETL")
        sys.exit(1)
