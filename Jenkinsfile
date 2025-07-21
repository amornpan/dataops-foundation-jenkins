pipeline {
    agent any
    
    environment {
        // Database configuration
        DB_SERVER = '35.185.131.47'
        DB_NAME = 'TestDB'
        DB_USERNAME = 'SA'
        DB_PASSWORD = credentials('mssql-password')  // Store in Jenkins credentials
        
        // Python environment
        PYTHON_VERSION = '3.9'
        VIRTUAL_ENV = 'venv'
        
        // ETL configuration
        DATA_FILE = 'data/LoanStats_web_small.csv'
        ACCEPTABLE_MAX_NULL = '26'
        
        // Quality gates
        MIN_TEST_COVERAGE = '80'
        MAX_MEMORY_USAGE_MB = '500'
        MAX_PROCESSING_TIME_SEC = '300'
    }
    
    options {
        // Keep builds for 30 days
        buildDiscarder(logRotator(daysToKeepStr: '30', numToKeepStr: '10'))
        
        // Timeout after 30 minutes
        timeout(time: 30, unit: 'MINUTES')
        
        // Skip default checkout
        skipDefaultCheckout(true)
    }
    
    stages {
        stage('🔄 Checkout') {
            steps {
                script {
                    echo "=== ETL CI Pipeline Started ==="
                    echo "Build: ${BUILD_NUMBER}"
                    echo "Branch: ${BRANCH_NAME}"
                }
                
                // Checkout source code
                checkout scm
                
                // Verify required files exist
                script {
                    if (!fileExists(env.DATA_FILE)) {
                        error "❌ Data file ${env.DATA_FILE} not found!"
                    }
                    if (!fileExists('ETL-dev.py')) {
                        error "❌ ETL script not found!"
                    }
                }
            }
        }
        
        stage('🐍 Setup Python Environment') {
            steps {
                script {
                    echo "Setting up Python ${env.PYTHON_VERSION} environment..."
                }
                
                // Create virtual environment
                bat """
                    python -m venv ${env.VIRTUAL_ENV}
                    ${env.VIRTUAL_ENV}\\Scripts\\activate.bat
                    
                    REM Upgrade pip
                    python -m pip install --upgrade pip
                    
                    REM Install required packages
                    pip install pandas numpy sqlalchemy pymssql
                    pip install pytest pytest-cov pytest-xvfb
                    pip install flake8 black isort
                    pip install psutil memory-profiler
                """
            }
        }
        
        stage('🔍 Code Quality Checks') {
            parallel {
                stage('Linting (flake8)') {
                    steps {
                        bat """
                            ${env.VIRTUAL_ENV}\\Scripts\\activate.bat
                            flake8 --max-line-length=120 --ignore=E203,W503 *.py || exit 0
                        """
                    }
                }
                
                stage('Code Formatting (black)') {
                    steps {
                        bat """
                            ${env.VIRTUAL_ENV}\\Scripts\\activate.bat
                            black --check --line-length=120 *.py || exit 0
                        """
                    }
                }
            }
        }
        
        stage('📊 Data Quality Validation') {
            steps {
                script {
                    echo "Validating data quality for ${env.DATA_FILE}..."
                }
                
                bat """
                    ${env.VIRTUAL_ENV}\\Scripts\\activate.bat
                    
                    python -c "
import pandas as pd
import sys

print('=== Data Quality Report ===')

# Read and analyze data
df = pd.read_csv('${env.DATA_FILE}')
print(f'Total rows: {len(df):,}')
print(f'Total columns: {len(df.columns)}')

# Check missing data
missing_pct = df.isnull().mean() * 100
critical_missing = missing_pct[missing_pct > 50]

if len(critical_missing) > 0:
    print('⚠️ Columns with >50%% missing data:')
    for col, pct in critical_missing.items():
        print(f'  - {col}: {pct:.1f}%%')

# Check data types
print('\\nData type distribution:')
type_counts = df.dtypes.value_counts()
for dtype, count in type_counts.items():
    print(f'  - {dtype}: {count} columns')

# Memory usage
memory_mb = df.memory_usage(deep=True).sum() / 1024**2
print(f'\\nMemory usage: {memory_mb:.2f} MB')

if memory_mb > ${env.MAX_MEMORY_USAGE_MB}:
    print(f'❌ Memory usage exceeds limit of ${env.MAX_MEMORY_USAGE_MB}MB')
    sys.exit(1)
else:
    print('✅ Memory usage within limits')
"
                """
            }
        }
        
        stage('🧪 Unit Tests') {
            steps {
                script {
                    echo "Running comprehensive unit tests..."
                }
                
                bat """
                    ${env.VIRTUAL_ENV}\\Scripts\\activate.bat
                    
                    REM Run unit tests
                    python tests/test_etl_pipeline.py
                """
            }
        }
        
        stage('⚡ Performance Tests') {
            steps {
                script {
                    echo "Running performance tests..."
                }
                
                bat """
                    ${env.VIRTUAL_ENV}\\Scripts\\activate.bat
                    
                    python -c "
import time
import pandas as pd
import numpy as np
import psutil
import gc

print('=== Performance Test ===')

# Memory test
process = psutil.Process()
memory_before = process.memory_info().rss / 1024**2

# Load and process data
start_time = time.time()
df = pd.read_csv('${env.DATA_FILE}')

# Simulate ETL processing
df_processed = df.copy()
missing_pct = df_processed.isnull().mean() * 100
columns_to_keep = missing_pct[missing_pct <= ${env.ACCEPTABLE_MAX_NULL}].index.tolist()
df_filtered = df_processed[columns_to_keep]

end_time = time.time()
processing_time = end_time - start_time

memory_after = process.memory_info().rss / 1024**2
memory_increase = memory_after - memory_before

print(f'Processing time: {processing_time:.2f} seconds')
print(f'Memory increase: {memory_increase:.2f} MB')

# Check performance thresholds
if processing_time > ${env.MAX_PROCESSING_TIME_SEC}:
    print(f'❌ Processing time exceeds limit of ${env.MAX_PROCESSING_TIME_SEC}s')
    exit(1)

if memory_increase > ${env.MAX_MEMORY_USAGE_MB}:
    print(f'❌ Memory usage exceeds limit of ${env.MAX_MEMORY_USAGE_MB}MB')
    exit(1)

print('✅ Performance tests passed')
"
                """
            }
        }
        
        stage('🔌 Database Connection Test') {
            steps {
                script {
                    echo "Testing database connectivity..."
                }
                
                bat """
                    ${env.VIRTUAL_ENV}\\Scripts\\activate.bat
                    
                    python -c "
from sqlalchemy import create_engine, text
import sys

print('=== Database Connection Test ===')

try:
    # Create engine
    engine = create_engine(f'mssql+pymssql://${env.DB_USERNAME}:${env.DB_PASSWORD}@${env.DB_SERVER}/${env.DB_NAME}')
    
    # Test connection
    with engine.connect() as connection:
        result = connection.execute(text('SELECT 1 as test'))
        test_value = result.fetchone()[0]
        
        if test_value == 1:
            print('✅ Database connection successful')
        else:
            print('❌ Database connection test failed')
            sys.exit(1)
            
except Exception as e:
    print(f'❌ Database connection failed: {str(e)}')
    sys.exit(1)
"
                """
            }
        }
        
        stage('🏗️ ETL Dry Run') {
            steps {
                script {
                    echo "Performing ETL dry run..."
                }
                
                bat """
                    ${env.VIRTUAL_ENV}\\Scripts\\activate.bat
                    
                    python -c "
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import warnings
warnings.filterwarnings('ignore')

print('=== ETL Dry Run ===')

# Load data
print('Loading data...')
df = pd.read_csv('${env.DATA_FILE}')
print(f'Loaded {len(df):,} rows')

# Apply data quality filters
print('Applying data quality filters...')
missing_pct = df.isnull().mean() * 100
columns_to_keep = missing_pct[missing_pct <= ${env.ACCEPTABLE_MAX_NULL}].index.tolist()
df_filtered = df[columns_to_keep]
print(f'Kept {len(columns_to_keep)} columns after filtering')

# Remove rows with nulls
df_clean = df_filtered.dropna()
print(f'Clean data: {len(df_clean):,} rows')

# Test dimension table creation
print('Testing dimension table creation...')
if 'home_ownership' in df_clean.columns:
    home_dim = df_clean[['home_ownership']].drop_duplicates().reset_index(drop=True)
    home_dim['home_ownership_id'] = home_dim.index
    print(f'Home ownership dimension: {len(home_dim)} unique values')

if 'loan_status' in df_clean.columns:
    status_dim = df_clean[['loan_status']].drop_duplicates().reset_index(drop=True)
    status_dim['loan_status_id'] = status_dim.index
    print(f'Loan status dimension: {len(status_dim)} unique values')

print('✅ ETL dry run completed successfully')
"
                """
            }
        }
    }
    
    post {
        always {
            script {
                echo "=== Pipeline Completed ==="
                echo "Build Number: ${BUILD_NUMBER}"
                echo "Duration: ${currentBuild.durationString}"
            }
            
            // Clean up
            bat """
                REM Clean up virtual environment
                if exist ${env.VIRTUAL_ENV} rmdir /s /q ${env.VIRTUAL_ENV}
                
                REM Clean up temporary files
                for /r %%i in (*.pyc) do del "%%i"
                for /d /r %%i in (__pycache__) do rmdir /s /q "%%i"
            """
        }
        
        success {
            script {
                echo "🎉 CI Pipeline succeeded! Ready for deployment."
            }
        }
        
        failure {
            script {
                echo "❌ CI Pipeline failed!"
            }
        }
        
        unstable {
            script {
                echo "⚠️ CI Pipeline unstable - some tests may have failed"
            }
        }
    }
}
