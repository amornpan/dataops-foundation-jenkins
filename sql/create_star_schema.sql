-- ===================================================================
-- Star Schema Creation Scripts for Loan Data Warehouse
-- Target Database: 35.185.131.47 (TestDB)
-- ===================================================================

-- ===================================================================
-- 1. DIMENSION TABLES
-- ===================================================================

-- Home Ownership Dimension Table
IF OBJECT_ID('home_ownership_dim', 'U') IS NOT NULL
    DROP TABLE home_ownership_dim;

CREATE TABLE home_ownership_dim (
    home_ownership_id INT IDENTITY(1,1) PRIMARY KEY,
    home_ownership NVARCHAR(50) NOT NULL UNIQUE,
    home_ownership_desc NVARCHAR(200),
    created_date DATETIME2 DEFAULT GETDATE(),
    updated_date DATETIME2 DEFAULT GETDATE(),
    
    -- Business metadata
    is_active BIT DEFAULT 1,
    data_source NVARCHAR(50) DEFAULT 'ETL_PIPELINE',
    
    -- Indexes for performance
    INDEX IX_home_ownership_dim_home_ownership (home_ownership),
    INDEX IX_home_ownership_dim_active (is_active)
);

-- Loan Status Dimension Table
IF OBJECT_ID('loan_status_dim', 'U') IS NOT NULL
    DROP TABLE loan_status_dim;

CREATE TABLE loan_status_dim (
    loan_status_id INT IDENTITY(1,1) PRIMARY KEY,
    loan_status NVARCHAR(50) NOT NULL UNIQUE,
    loan_status_desc NVARCHAR(200),
    status_category NVARCHAR(50), -- 'ACTIVE', 'CLOSED', 'DEFAULT'
    is_performing BIT, -- 1 for performing loans, 0 for non-performing
    created_date DATETIME2 DEFAULT GETDATE(),
    updated_date DATETIME2 DEFAULT GETDATE(),
    
    -- Business metadata
    is_active BIT DEFAULT 1,
    data_source NVARCHAR(50) DEFAULT 'ETL_PIPELINE',
    
    -- Indexes for performance
    INDEX IX_loan_status_dim_loan_status (loan_status),
    INDEX IX_loan_status_dim_category (status_category),
    INDEX IX_loan_status_dim_performing (is_performing)
);

-- Issue Date Dimension Table (Enhanced with date attributes)
IF OBJECT_ID('issue_d_dim', 'U') IS NOT NULL
    DROP TABLE issue_d_dim;

CREATE TABLE issue_d_dim (
    issue_d_id INT IDENTITY(1,1) PRIMARY KEY,
    issue_d DATE NOT NULL UNIQUE,
    
    -- Date components
    year INT NOT NULL,
    quarter INT NOT NULL,
    month INT NOT NULL,
    day INT NOT NULL,
    
    -- Computed columns for better analytics
    month_name AS (DATENAME(MONTH, issue_d)),
    day_name AS (DATENAME(WEEKDAY, issue_d)),
    day_of_year AS (DATEPART(DAYOFYEAR, issue_d)),
    week_of_year AS (DATEPART(WEEK, issue_d)),
    
    -- Business calendar attributes
    is_weekend AS (CASE WHEN DATEPART(WEEKDAY, issue_d) IN (1, 7) THEN 1 ELSE 0 END),
    is_month_end AS (CASE WHEN issue_d = EOMONTH(issue_d) THEN 1 ELSE 0 END),
    is_quarter_end AS (CASE WHEN month IN (3, 6, 9, 12) AND issue_d = EOMONTH(issue_d) THEN 1 ELSE 0 END),
    is_year_end AS (CASE WHEN month = 12 AND issue_d = EOMONTH(issue_d) THEN 1 ELSE 0 END),
    
    -- Fiscal year (assuming April-March fiscal year)
    fiscal_year AS (CASE WHEN month >= 4 THEN year ELSE year - 1 END),
    fiscal_quarter AS (
        CASE 
            WHEN month BETWEEN 4 AND 6 THEN 1
            WHEN month BETWEEN 7 AND 9 THEN 2
            WHEN month BETWEEN 10 AND 12 THEN 3
            ELSE 4
        END
    ),
    
    -- Metadata
    created_date DATETIME2 DEFAULT GETDATE(),
    updated_date DATETIME2 DEFAULT GETDATE(),
    is_active BIT DEFAULT 1,
    data_source NVARCHAR(50) DEFAULT 'ETL_PIPELINE',
    
    -- Indexes for performance
    INDEX IX_issue_d_dim_date (issue_d),
    INDEX IX_issue_d_dim_year_month (year, month),
    INDEX IX_issue_d_dim_quarter (year, quarter),
    INDEX IX_issue_d_dim_fiscal (fiscal_year, fiscal_quarter)
);

-- ===================================================================
-- 2. FACT TABLE
-- ===================================================================

-- Loans Fact Table (Enhanced with additional metrics)
IF OBJECT_ID('loans_fact', 'U') IS NOT NULL
    DROP TABLE loans_fact;

CREATE TABLE loans_fact (
    loan_fact_id BIGINT IDENTITY(1,1) PRIMARY KEY,
    
    -- Foreign Keys to Dimensions
    home_ownership_id INT NOT NULL,
    loan_status_id INT NOT NULL,
    issue_d_id INT NOT NULL,
    
    -- Loan Details
    application_type NVARCHAR(50),
    loan_amnt DECIMAL(18,2) NOT NULL,
    funded_amnt DECIMAL(18,2) NOT NULL,
    term NVARCHAR(20),
    int_rate DECIMAL(8,6) NOT NULL,
    installment DECIMAL(18,2) NOT NULL,
    
    -- Calculated Metrics
    funding_ratio AS (funded_amnt / NULLIF(loan_amnt, 0)),
    monthly_payment_ratio AS (installment / NULLIF(loan_amnt, 0)),
    annual_payment_amount AS (installment * 12),
    
    -- Data Quality Flags
    data_quality_score TINYINT DEFAULT 100, -- 0-100 quality score
    has_data_issues BIT DEFAULT 0,
    validation_errors NVARCHAR(500),
    
    -- ETL Metadata
    created_date DATETIME2 DEFAULT GETDATE(),
    updated_date DATETIME2 DEFAULT GETDATE(),
    etl_batch_id NVARCHAR(50),
    data_source NVARCHAR(50) DEFAULT 'ETL_PIPELINE',
    
    -- Foreign Key Constraints
    CONSTRAINT FK_loans_fact_home_ownership 
        FOREIGN KEY (home_ownership_id) REFERENCES home_ownership_dim(home_ownership_id),
    CONSTRAINT FK_loans_fact_loan_status 
        FOREIGN KEY (loan_status_id) REFERENCES loan_status_dim(loan_status_id),
    CONSTRAINT FK_loans_fact_issue_d 
        FOREIGN KEY (issue_d_id) REFERENCES issue_d_dim(issue_d_id),
    
    -- Business Rules Constraints
    CONSTRAINT CHK_loans_fact_loan_amnt_positive CHECK (loan_amnt > 0),
    CONSTRAINT CHK_loans_fact_funded_amnt_positive CHECK (funded_amnt > 0),
    CONSTRAINT CHK_loans_fact_funded_le_loan CHECK (funded_amnt <= loan_amnt),
    CONSTRAINT CHK_loans_fact_int_rate_valid CHECK (int_rate >= 0 AND int_rate <= 1),
    CONSTRAINT CHK_loans_fact_installment_positive CHECK (installment > 0),
    
    -- Performance Indexes
    INDEX IX_loans_fact_home_ownership (home_ownership_id),
    INDEX IX_loans_fact_loan_status (loan_status_id),
    INDEX IX_loans_fact_issue_d (issue_d_id),
    INDEX IX_loans_fact_loan_amnt (loan_amnt),
    INDEX IX_loans_fact_int_rate (int_rate),
    INDEX IX_loans_fact_created_date (created_date),
    
    -- Composite indexes for common query patterns
    INDEX IX_loans_fact_composite_date_amount (issue_d_id, loan_amnt),
    INDEX IX_loans_fact_composite_status_rate (loan_status_id, int_rate),
    INDEX IX_loans_fact_composite_home_date (home_ownership_id, issue_d_id)
);

-- ===================================================================
-- 3. ANALYTICAL VIEWS
-- ===================================================================

-- Comprehensive Loan Summary View
CREATE OR ALTER VIEW vw_loan_summary AS
SELECT 
    h.home_ownership,
    h.home_ownership_desc,
    s.loan_status,
    s.status_category,
    s.is_performing,
    d.year,
    d.quarter,
    d.month,
    d.month_name,
    d.fiscal_year,
    d.fiscal_quarter,
    
    -- Volume Metrics
    COUNT(*) as loan_count,
    COUNT(*) * 1.0 / SUM(COUNT(*)) OVER() as loan_percentage,
    
    -- Amount Metrics
    SUM(f.loan_amnt) as total_loan_amount,
    SUM(f.funded_amnt) as total_funded_amount,
    AVG(f.loan_amnt) as avg_loan_amount,
    AVG(f.funded_amnt) as avg_funded_amount,
    MIN(f.loan_amnt) as min_loan_amount,
    MAX(f.loan_amnt) as max_loan_amount,
    STDEV(f.loan_amnt) as stddev_loan_amount,
    
    -- Rate Metrics
    AVG(f.int_rate) as avg_interest_rate,
    MIN(f.int_rate) as min_interest_rate,
    MAX(f.int_rate) as max_interest_rate,
    STDEV(f.int_rate) as stddev_interest_rate,
    
    -- Payment Metrics
    SUM(f.installment) as total_monthly_payment,
    AVG(f.installment) as avg_monthly_payment,
    SUM(f.annual_payment_amount) as total_annual_payment,
    
    -- Funding Metrics
    AVG(f.funding_ratio) as avg_funding_ratio,
    SUM(CASE WHEN f.funding_ratio = 1 THEN 1 ELSE 0 END) as fully_funded_count,
    AVG(f.monthly_payment_ratio) as avg_payment_to_loan_ratio

FROM loans_fact f
JOIN home_ownership_dim h ON f.home_ownership_id = h.home_ownership_id
JOIN loan_status_dim s ON f.loan_status_id = s.loan_status_id
JOIN issue_d_dim d ON f.issue_d_id = d.issue_d_id
GROUP BY 
    h.home_ownership, h.home_ownership_desc,
    s.loan_status, s.status_category, s.is_performing,
    d.year, d.quarter, d.month, d.month_name,
    d.fiscal_year, d.fiscal_quarter;

-- Monthly Trends View
CREATE OR ALTER VIEW vw_monthly_trends AS
SELECT 
    d.year,
    d.month,
    d.month_name,
    d.quarter,
    d.fiscal_year,
    d.fiscal_quarter,
    
    -- Volume Trends
    COUNT(*) as loan_count,
    COUNT(*) - LAG(COUNT(*)) OVER (ORDER BY d.year, d.month) as loan_count_change,
    
    -- Amount Trends
    SUM(f.loan_amnt) as total_volume,
    AVG(f.loan_amnt) as avg_loan_size,
    SUM(f.loan_amnt) - LAG(SUM(f.loan_amnt)) OVER (ORDER BY d.year, d.month) as volume_change,
    
    -- Rate Trends
    AVG(f.int_rate) as avg_rate,
    AVG(f.int_rate) - LAG(AVG(f.int_rate)) OVER (ORDER BY d.year, d.month) as rate_change,
    
    -- Portfolio Composition
    COUNT(CASE WHEN h.home_ownership = 'RENT' THEN 1 END) as rent_count,
    COUNT(CASE WHEN h.home_ownership = 'OWN' THEN 1 END) as own_count,
    COUNT(CASE WHEN h.home_ownership = 'MORTGAGE' THEN 1 END) as mortgage_count,
    
    -- Performance Indicators
    COUNT(CASE WHEN s.is_performing = 1 THEN 1 END) as performing_loans,
    COUNT(CASE WHEN s.is_performing = 0 THEN 1 END) as non_performing_loans,
    COUNT(CASE WHEN s.is_performing = 1 THEN 1 END) * 1.0 / COUNT(*) as performing_rate

FROM loans_fact f
JOIN home_ownership_dim h ON f.home_ownership_id = h.home_ownership_id
JOIN loan_status_dim s ON f.loan_status_id = s.loan_status_id
JOIN issue_d_dim d ON f.issue_d_id = d.issue_d_id
GROUP BY d.year, d.month, d.month_name, d.quarter, d.fiscal_year, d.fiscal_quarter;

-- ===================================================================
-- 4. STORED PROCEDURES FOR MAINTENANCE
-- ===================================================================

-- Procedure to refresh statistics
CREATE OR ALTER PROCEDURE sp_refresh_warehouse_statistics
AS
BEGIN
    SET NOCOUNT ON;
    
    PRINT 'Refreshing statistics for data warehouse tables...';
    
    UPDATE STATISTICS home_ownership_dim;
    UPDATE STATISTICS loan_status_dim;
    UPDATE STATISTICS issue_d_dim;
    UPDATE STATISTICS loans_fact;
    
    PRINT 'Statistics refresh completed.';
END;

-- Procedure to rebuild indexes
CREATE OR ALTER PROCEDURE sp_rebuild_warehouse_indexes
AS
BEGIN
    SET NOCOUNT ON;
    
    PRINT 'Rebuilding indexes for data warehouse tables...';
    
    ALTER INDEX ALL ON home_ownership_dim REBUILD;
    ALTER INDEX ALL ON loan_status_dim REBUILD;
    ALTER INDEX ALL ON issue_d_dim REBUILD;
    ALTER INDEX ALL ON loans_fact REBUILD;
    
    PRINT 'Index rebuild completed.';
END;

-- Procedure for data quality checks
CREATE OR ALTER PROCEDURE sp_data_quality_check
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @TotalRecords INT;
    DECLARE @IssueCount INT;
    DECLARE @IssuePercentage DECIMAL(5,2);
    
    SELECT @TotalRecords = COUNT(*) FROM loans_fact;
    SELECT @IssueCount = COUNT(*) FROM loans_fact WHERE has_data_issues = 1;
    SET @IssuePercentage = (@IssueCount * 100.0) / NULLIF(@TotalRecords, 0);
    
    PRINT 'Data Quality Check Results:';
    PRINT '==========================';
    PRINT 'Total Records: ' + CAST(@TotalRecords AS VARCHAR(20));
    PRINT 'Records with Issues: ' + CAST(@IssueCount AS VARCHAR(20));
    PRINT 'Issue Percentage: ' + CAST(@IssuePercentage AS VARCHAR(10)) + '%';
    
    IF @IssuePercentage > 5.0
    BEGIN
        PRINT 'WARNING: Data quality issues exceed 5% threshold!';
    END
    ELSE
    BEGIN
        PRINT 'Data quality is within acceptable limits.';
    END
END;

PRINT 'Star schema creation completed successfully!';
PRINT 'Tables created: home_ownership_dim, loan_status_dim, issue_d_dim, loans_fact';
PRINT 'Views created: vw_loan_summary, vw_monthly_trends';
PRINT 'Stored procedures created: sp_refresh_warehouse_statistics, sp_rebuild_warehouse_indexes, sp_data_quality_check';
