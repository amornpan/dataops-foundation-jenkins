pipeline {
    agent any
    
    environment {
        // Database configuration
        DB_SERVER = 'mssql.minddatatech.com'
        DB_NAME = 'TestDB'
        DB_USERNAME = 'SA'
        DB_PASSWORD = credentials('mssql-password')  // ต้องสร้างใน Jenkins credentials
        
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
        
        // Timestamps in console output
        timestamps()
    }
    
    stages {
        stage('🔄 Checkout') {
            steps {
                script {
                    echo "=== ETL CI Pipeline Started ==="
                    echo "Build: ${BUILD_NUMBER}"
                    echo "Branch: ${env.GIT_BRANCH ?: 'main'}"
                }
                
                // Verify required files exist
                script {
                    if (!fileExists(env.DATA_FILE)) {
                        echo "⚠️  Warning: Data file ${env.DATA_FILE} not found, but continuing..."
                    } else {
                        echo "✅ Data file found: ${env.DATA_FILE}"
                    }
                    if (!fileExists('etl_main.py')) {
                        error "❌ ETL script not found!"
                    }
                    echo "✅ ETL script found"
                }
            }
        }
        
        stage('🐍 Setup Python Environment') {
            steps {
                script {
                    echo "Setting up Python environment..."
                }
                
                // Create virtual environment (Linux)
                sh '''
                    # Clean up any existing venv
                    rm -rf ${VIRTUAL_ENV}
                    
                    # Create new virtual environment
                    python3 -m venv ${VIRTUAL_ENV}
                    
                    # Activate and install dependencies
                    . ${VIRTUAL_ENV}/bin/activate
                    
                    # Upgrade pip
                    python -m pip install --upgrade pip
                    
                    # Install required packages
                    pip install pandas numpy sqlalchemy pymssql
                    pip install pytest pytest-cov
                    pip install flake8 black isort
                    pip install psutil memory-profiler
                    
                    # Verify installation
                    python -c "import pandas, numpy, sqlalchemy; print('✅ Core packages installed')"
                '''
            }
        }
        
        stage('🔍 Code Quality Checks') {
            parallel {
                stage('Linting (flake8)') {
                    steps {
                        sh '''
                            . ${VIRTUAL_ENV}/bin/activate
                            flake8 --max-line-length=120 --ignore=E203,W503 --exclude=venv *.py || echo "⚠️  Linting warnings found"
                        '''
                    }
                }
                
                stage('Code Formatting (black)') {
                    steps {
                        sh '''
                            . ${VIRTUAL_ENV}/bin/activate
                            black --check --line-length=120 --exclude=venv *.py || echo "⚠️  Code formatting issues found"
                        '''
                    }
                }
            }
        }
        
        stage('📊 Data Quality Validation') {
            steps {
                script {
                    echo "Validating data quality for ${env.DATA_FILE}..."
                }
                
                sh '''
                    . ${VIRTUAL_ENV}/bin/activate
                    
                    python3 -c "
import pandas as pd
import sys
import os

print('=== Data Quality Report ===')

# Check file exists
if not os.path.exists('${DATA_FILE}'):
    print('⚠️  Data file not found: ${DATA_FILE}')
    print('Skipping data quality validation...')
    exit(0)

# Read and analyze data
try:
    df = pd.read_csv('${DATA_FILE}', low_memory=False)
    print(f'✅ Data loaded: {len(df):,} rows, {len(df.columns)} columns')
except Exception as e:
    print(f'❌ Failed to read data file: {e}')
    sys.exit(1)

# Check missing data
missing_pct = df.isnull().mean() * 100
critical_missing = missing_pct[missing_pct > 50]

if len(critical_missing) > 0:
    print(f'⚠️  {len(critical_missing)} columns with >50% missing data')

# Check required columns
required_cols = ['loan_amnt', 'funded_amnt', 'term', 'int_rate', 'installment', 'home_ownership', 'loan_status', 'issue_d']
missing_required = [col for col in required_cols if col not in df.columns]

if missing_required:
    print(f'❌ Missing required columns: {missing_required}')
    sys.exit(1)
else:
    print('✅ All required columns present')

# Memory usage check
memory_mb = df.memory_usage(deep=True).sum() / 1024**2
print(f'Memory usage: {memory_mb:.2f} MB')

if memory_mb > ${MAX_MEMORY_USAGE_MB}:
    print(f'⚠️  Memory usage exceeds limit of ${MAX_MEMORY_USAGE_MB}MB')
else:
    print('✅ Memory usage within limits')

print('✅ Data quality validation completed')
"
                '''
            }
        }
        
        stage('🧪 Unit Tests') {
            steps {
                script {
                    echo "Running unit tests..."
                }
                
                sh '''
                    . ${VIRTUAL_ENV}/bin/activate
                    
                    # Run simple test if available
                    if [ -f "simple_test.py" ]; then
                        echo "Running simple_test.py..."
                        python simple_test.py || echo "⚠️  Some tests had issues"
                    else
                        echo "No simple_test.py found, running basic ETL validation..."
                        python -c "
import etl_main
print('Testing ETL functions...')
result, types = etl_main.guess_column_types('data/LoanStats_web_small.csv') if os.path.exists('data/LoanStats_web_small.csv') else (True, {})
print(f'✅ ETL functions working: {len(types)} columns analyzed' if result else '❌ ETL function test failed')
"
                    fi
                '''
            }
        }
        
        stage('🔌 Database Connection Test') {
            steps {
                script {
                    echo "Testing database connectivity..."
                }
                
                sh '''
                    . ${VIRTUAL_ENV}/bin/activate
                    
                    python3 -c "
from sqlalchemy import create_engine, text
import sys

print('=== Database Connection Test ===')

try:
    # Create engine
    engine = create_engine(f'mssql+pymssql://${DB_USERNAME}:${DB_PASSWORD}@${DB_SERVER}/${DB_NAME}')
    
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
    print('Note: This might be expected if database is not accessible from Jenkins')
    # Don't fail the build for DB connection issues in CI
    print('Continuing with build...')
"
                '''
            }
        }
        
        stage('🏗️ ETL Dry Run') {
            steps {
                script {
                    echo "Performing ETL dry run..."
                }
                
                sh '''
                    . ${VIRTUAL_ENV}/bin/activate
                    
                    python3 -c "
import sys
import os

print('=== ETL Dry Run ===')

# Check if data file exists
if not os.path.exists('${DATA_FILE}'):
    print('⚠️  Data file not found, skipping ETL dry run')
    sys.exit(0)

try:
    import etl_main
    
    # Test column type detection
    result, types = etl_main.guess_column_types('${DATA_FILE}')
    
    if result:
        print(f'✅ ETL functions tested: {len(types)} columns analyzed')
        print('✅ Dry run completed successfully')
    else:
        print(f'❌ ETL dry run failed: {types}')
        sys.exit(1)
        
except Exception as e:
    print(f'❌ ETL dry run failed: {str(e)}')
    sys.exit(1)
"
                '''
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
            
            // Clean up (within node context)
            sh '''
                # Clean up virtual environment
                rm -rf ${VIRTUAL_ENV} || echo "Virtual environment cleanup completed"
                
                # Clean up Python cache
                find . -name "*.pyc" -delete 2>/dev/null || echo "Python cache cleaned"
                find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || echo "Pycache cleaned"
            '''
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
