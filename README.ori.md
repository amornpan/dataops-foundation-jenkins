# DataOps Foundation Jenkins Project

ETL Pipeline โปรเจคสำหรับประมวลผลข้อมูล Loan Statistics และสร้าง Star Schema บน SQL Server

## 📁 โครงสร้างโปรเจค

```
dataops-foundation-jenkins/
├── 📄 README.md                     # เอกสารนี้
├── 📄 requirements.txt              # Python dependencies
├── 📄 Jenkinsfile                   # CI Pipeline
├── 📄 etl_main.py                   # ETL Script หลัก
├── 
├── 📁 data/                         # ไฟล์ข้อมูล
│   └── 📄 LoanStats_web_small.csv   # ข้อมูลต้นฉบับ (ต้องคัดลอกมาวางเอง)
├── 
├── 📁 tests/                        # Unit Tests
│   └── 📄 test_etl_pipeline.py      # การทดสอบ ETL
├── 
├── 📁 sql/                          # SQL Scripts
│   └── 📄 create_star_schema.sql    # สร้าง Star Schema
├── 
├── 📁 config/                       # Configuration Files
│   ├── 📄 database.yaml             # การตั้งค่าฐานข้อมูล
│   └── 📄 etl_config.yaml          # การตั้งค่า ETL
├── 
└── 📁 backups/                      # โฟลเดอร์สำหรับ Backup (สร้างอัตโนมัติ)
```

## 🚀 การติดตั้งและใช้งาน

### 1. เตรียมข้อมูล
```bash
# คัดลอกไฟล์ข้อมูลจากโฟลเดอร์เดิม
copy "C:\Users\Asus\dataops-foundation\LoanStats_web_small.csv" "data\"
```

### 2. ติดตั้ง Dependencies
```bash
# สร้าง virtual environment
python -m venv venv
venv\Scripts\activate

# ติดตั้ง packages
pip install -r requirements.txt
```

### 3. รัน ETL Pipeline
```bash
# รัน ETL แบบ manual
python etl_main.py

# รัน Unit Tests
python tests/test_etl_pipeline.py
```

### 4. ตั้งค่า Database
```sql
-- เชื่อมต่อไปยัง mssql.minddatatech.com ด้วย SA user
-- รัน SQL Script
sqlcmd -S mssql.minddatatech.com -U SA -P Passw0rd123456 -d TestDB -i sql/create_star_schema.sql
```

## 🎯 คุณสมบัติหลัก

### ETL Pipeline Features
- ✅ **Data Quality Checking**: ตรวจสอบ missing data และกรองข้อมูล
- ✅ **Data Transformation**: แปลง date, percentage และ data types
- ✅ **Star Schema Creation**: สร้าง dimension และ fact tables
- ✅ **Database Loading**: โหลดข้อมูลไปยัง SQL Server
- ✅ **Error Handling**: จัดการข้อผิดพลาดและ validation

### Unit Testing Features
- ✅ **Real Data Testing**: ใช้ข้อมูลจริงจาก CSV file
- ✅ **Data Quality Tests**: ทดสอบคุณภาพข้อมูล
- ✅ **ETL Logic Tests**: ทดสอบขั้นตอน ETL ทั้งหมด
- ✅ **Business Rules Tests**: ทดสอบ business logic
- ✅ **Performance Tests**: ทดสอบประสิทธิภาพการประมวลผล

### CI/CD Features
- ✅ **Jenkins Pipeline**: CI/CD automation
- ✅ **Code Quality Checks**: Linting และ formatting
- ✅ **Automated Testing**: รัน unit tests อัตโนมัติ
- ✅ **Database Validation**: ทดสอบการเชื่อมต่อฐานข้อมูล
- ✅ **Performance Monitoring**: ตรวจสอบ memory และเวลาประมวลผล

## 📊 Star Schema Design

### Dimension Tables
- **home_ownership_dim**: ประเภทการเป็นเจ้าของบ้าน
- **loan_status_dim**: สถานะของสินเชื่อ
- **issue_d_dim**: วันที่ออกสินเชื่อ (พร้อม date attributes)

### Fact Table
- **loans_fact**: ข้อมูลสินเชื่อหลักพร้อม calculated metrics

### Analytical Views
- **vw_loan_summary**: สรุปข้อมูลสินเชื่อแบบรายละเอียด
- **vw_monthly_trends**: แนวโน้มรายเดือน

## 🔧 การตั้งค่า Jenkins

### 1. สร้าง Credentials
- **ID**: `mssql-password`
- **Type**: Secret text
- **Value**: `Passw0rd123456`

### 2. สร้าง Pipeline Job
- **Job Name**: `etl-ci-pipeline`
- **Type**: Pipeline
- **Script**: ใช้ Jenkinsfile ในโปรเจค

## 📈 ตัวอย่างการใช้งาน

### รัน ETL Pipeline
```python
# Import และรัน ETL
from etl_main import main
main()
```

### Query ข้อมูลจาก Star Schema
```sql
-- ดูสรุปสินเชื่อตาม home ownership
SELECT * FROM vw_loan_summary 
WHERE year = 2023
ORDER BY total_loan_amount DESC;

-- ดูแนวโน้มรายเดือน
SELECT * FROM vw_monthly_trends
ORDER BY year DESC, month DESC;
```

### รัน Unit Tests
```bash
# รัน tests ทั้งหมด
python tests/test_etl_pipeline.py

# ผลลัพธ์จะแสดงสถิติข้อมูลจริง
```

## ⚙️ การกำหนดค่า

### Database Configuration
แก้ไขไฟล์ `config/database.yaml`:
```yaml
database:
  development:
    server: "mssql.minddatatech.com"
    database: "TestDB"
    username: "SA"
```

### ETL Configuration
แก้ไขไฟล์ `config/etl_config.yaml`:
```yaml
etl:
  data_quality:
    max_missing_percentage: 30
    acceptable_max_null: 26
```

## 🐛 การแก้ไขปัญหา

### ปัญหาทั่วไป

1. **ไม่พบไฟล์ CSV**
   ```
   FileNotFoundError: ไม่พบไฟล์ data/LoanStats_web_small.csv
   ```
   **วิธีแก้**: คัดลอกไฟล์ CSV ไปวางในโฟลเดอร์ `data/`

2. **Database Connection Error**
   ```
   Database connection failed
   ```
   **วิธีแก้**: ตรวจสอบ network connectivity และ credentials

3. **Memory Error**
   ```
   Memory usage exceeds limit
   ```
   **วิธีแก้**: ลดขนาด chunk_size ในการประมวลผล

## 📞 การสนับสนุน

- ตรวจสอบ logs ใน Jenkins build
- ดู database error logs
- ทดสอบส่วนประกอบแยกส่วนเพื่อหาปัญหา
- ตรวจสอบ system resources ระหว่างการรัน ETL

## 🎉 การพัฒนาต่อ

### ขั้นตอนต่อไป
1. เพิ่ม data validation rules
2. สร้าง dashboard สำหรับ monitoring
3. เพิ่ม incremental loading
4. ปรับปรุง performance optimization
5. เพิ่ม alerting และ notification

---

**หมายเหตุ**: โปรเจคนี้ใช้ข้อมูลจริงจาก LoanStats_web_small.csv และเชื่อมต่อกับ SQL Server ที่ mssql.minddatatech.com
