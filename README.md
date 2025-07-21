# ภาพประกอบการใช้งาน Jenkins Pipeline

## 📸 หน้าจอสำคัญที่คุณจะเห็น

### 1. หน้า Jenkins Dashboard
```
┌─────────────────────────────────────────────────────────┐
│ Jenkins                                    [🔧] [👤] [?] │
├─────────────────────────────────────────────────────────┤
│ 🆕 New Item    📊 People    📈 Build History             │
├─────────────────────────────────────────────────────────┤
│ Jobs:                                                   │
│ ✅ etl-ci-pipeline        #5  ⏰ 2 min ago   🟢 Success │
│ ❌ backup-job            #2  ⏰ 1 hr ago    🔴 Failed   │
│ ⚠️ test-pipeline         #8  ⏰ 5 min ago   🟡 Unstable │
└─────────────────────────────────────────────────────────┘
```

### 2. หน้า New Item
```
┌─────────────────────────────────────────────────────────┐
│ Enter an item name: [etl-ci-pipeline          ]         │
│                                                         │
│ 📁 Freestyle project                                   │
│ 🔄 Pipeline                          ← เลือกอันนี้      │
│ 📂 Multi-configuration project                         │
│ 📋 Folder                                              │
│                                                         │
│ [OK]  [Cancel]                                         │
└─────────────────────────────────────────────────────────┘
```

### 3. หน้า Pipeline Configuration
```
┌─────────────────────────────────────────────────────────┐
│ General                                                 │
│ ☑ Discard old builds                                   │
│   Days to keep builds: [30]                            │
│   Max # of builds: [20]                                │
│                                                         │
│ Build Triggers                                          │
│ ☑ Poll SCM: [H/5 * * * *]                             │
│                                                         │
│ Pipeline                                                │
│ Definition: [Pipeline script from SCM ▼]               │
│ SCM: [Git ▼]                                           │
│ Repository URL: [https://github.com/amornpan/...]      │
│ Credentials: [github-credentials ▼]                    │
│ Branch: [*/main]                                        │
│ Script Path: [Jenkinsfile]                             │
│                                                         │
│ [Save]  [Apply]  [Cancel]                              │
└─────────────────────────────────────────────────────────┘
```

### 4. หน้า Add Credentials
```
┌─────────────────────────────────────────────────────────┐
│ Kind: [Secret text ▼]                                  │
│ Scope: [Global ▼]                                      │
│ Secret: [••••••••••••••••••••••••••••••••••••••••••••] │
│ ID: [mssql-password]                                   │
│ Description: [SQL Server Password for ETL Pipeline]    │
│                                                         │
│ [OK]  [Cancel]                                         │
└─────────────────────────────────────────────────────────┘
```

### 5. หน้า Build Console Output
```
Started by user Jenkins Admin
Running in Dockerfile agent

[Pipeline] Start of Pipeline
[Pipeline] stage
[Pipeline] { (🔄 Checkout)
[Pipeline] echo
=== ETL CI Pipeline Started ===
[Pipeline] echo
Build: 5
[Pipeline] echo
Branch: main
[Pipeline] script
[Pipeline] {
[Pipeline] fileExists
[Pipeline] echo
✅ ETL script found
[Pipeline] }
[Pipeline] // script
[Pipeline] }
[Pipeline] // stage

[Pipeline] stage
[Pipeline] { (🐍 Setup Python Environment)
[Pipeline] echo
Setting up Python environment...
[Pipeline] sh
+ rm -rf venv
+ python3 -m venv venv
+ . venv/bin/activate
+ python -m pip install --upgrade pip
✅ Core packages installed
[Pipeline] }
[Pipeline] // stage

[Pipeline] stage
[Pipeline] { (🧪 Unit Tests)
[Pipeline] echo
Running jenkins_test.py...
[Pipeline] sh
=== Jenkins-Friendly ETL Tests ===
--- Basic Imports ---
✅ Core packages imported successfully
--- ETL Functions ---
✅ ETL function test passed: 144 columns
--- Database Connection ---
⚠️ Database connection failed: connection timeout
Note: This is expected if running in CI
===============================================
📊 Test Results Summary:
   Basic Imports: ✅ PASS
   ETL Functions: ✅ PASS  
   Database Connection: ✅ PASS
Overall: 3/3 tests passed (100%)
🎉 Tests completed successfully!
[Pipeline] }
[Pipeline] // stage

[Pipeline] stage
[Pipeline] { (Declarative: Post Actions)
[Pipeline] script
[Pipeline] {
[Pipeline] echo
=== Pipeline Completed ===
[Pipeline] echo
Build Number: 5
[Pipeline] echo
Duration: 2 min 34 sec
[Pipeline] }
[Pipeline] // script
[Pipeline] echo
🎉 CI Pipeline succeeded! Ready for deployment.
[Pipeline] }
[Pipeline] // stage
[Pipeline] End of Pipeline
Finished: SUCCESS
```

### 6. หน้า Blue Ocean View
```
┌─────────────────────────────────────────────────────────┐
│ etl-ci-pipeline                                  #5     │
├─────────────────────────────────────────────────────────┤
│ [🔄]─[🐍]─[🔍]─[📊]─[🧪]─[🔌]─[🏗️]                    │
│  2s   25s  15s  8s   12s  5s   7s                      │
│  ✅   ✅   ⚠️   ✅   ✅   ⚠️   ✅                        │
│                                                         │
│ Total Duration: 2m 34s                                 │
│ Status: ✅ SUCCESS                                     │
└─────────────────────────────────────────────────────────┘
```

## 🎯 ขั้นตอนการใช้งานจริง (Step by Step)

### การรัน Pipeline ครั้งแรก

#### Step 1: เข้าสู่ Jenkins
1. เปิดเบราว์เซอร์ไปที่: `http://your-jenkins-server:8080`
2. Login ด้วย username/password ที่สร้างไว้
3. คุณจะเห็นหน้า Dashboard

#### Step 2: เลือก Pipeline Job
1. ในหน้า Dashboard คลิกที่ `etl-ci-pipeline`
2. คุณจะเห็นหน้าประวัติ builds ของ job นี้

#### Step 3: รัน Build
1. คลิกปุ่ม **"Build Now"** ทางซ้าย
2. Build ใหม่จะปรากฏใน **Build History**
3. คลิกที่หมายเลข build (เช่น `#1`) เพื่อดูรายละเอียด

#### Step 4: ดู Console Output
1. ในหน้า build คลิก **"Console Output"**
2. คุณจะเห็นข้อความแบบ real-time ของการทำงาน
3. รอจน pipeline ทำงานเสร็จ

### การแปลผลลัพธ์

#### Build สำเร็จ (🟢 SUCCESS)
```
✅ ทุก stage ผ่านหมด
✅ สีเขียวใน build history
✅ ข้อความ "🎉 CI Pipeline succeeded!"
```

#### Build ล้มเหลว (🔴 FAILED)
```
❌ มี stage ที่ล้มเหลว
❌ สีแดงใน build history  
❌ ข้อความ "❌ CI Pipeline failed!"
❌ ดู Console Output เพื่อหาสาเหตุ
```

#### Build ไม่เสถียร (🟡 UNSTABLE)
```
⚠️ บาง test ผ่าน บาง test ล้มเหลว
⚠️ สีเหลืองใน build history
⚠️ ข้อความ "⚠️ CI Pipeline unstable"
```

## 🛠️ การแก้ไขปัญหาเบื้องต้น

### ปัญหา: Build ติด "Pending"
**อาการ**: Build ไม่เริ่มทำงาน ค้างที่สถานะ "Pending"

**สาเหตุ**:
- Jenkins agent ไม่พร้อม
- Resource ไม่เพียงพอ

**วิธีแก้**:
1. ตรวจสอบ **Manage Jenkins** → **Manage Nodes**
2. ดูว่า agent online หรือไม่
3. รีสตาร์ท Jenkins ถ้าจำเป็น

### ปัญหา: "Credentials not found"
**อาการ**: 
```
ERROR: mssql-password
Finished: FAILURE
```

**วิธีแก้**:
1. ไป **Manage Jenkins** → **Manage Credentials**
2. ตรวจสอบว่ามี credential ID ที่ถูกต้อง
3. สร้าง credential ใหม่ถ้าจำเป็น

### ปัญหา: Python Module ไม่พบ
**อาการ**:
```
ModuleNotFoundError: No module named 'pandas'
```

**วิธีแก้**:
1. ตรวจสอบ virtual environment ใน pipeline
2. ดู Console Output ส่วน "Setup Python Environment"
3. แก้ไข requirements.txt ถ้าจำเป็น

## 📊 การ Monitor และ Maintenance

### การดู Trends
```
Jenkins Dashboard → etl-ci-pipeline → Trend
```
คุณจะเห็น:
- Build success rate
- Build duration trends
- Test result trends

### การตั้งค่า Notifications
1. **Configure job** → **Post-build Actions**
2. เพิ่ม **E-mail Notification**
3. กรอก email addresses ที่ต้องการแจ้งเตือน

### การ Backup
```bash
# Backup Jenkins configuration
docker exec jenkins-etl tar -czf /tmp/jenkins-backup.tar.gz /var/jenkins_home

# Copy ออกมา
docker cp jenkins-etl:/tmp/jenkins-backup.tar.gz ./
```

## 🎯 Next Steps

เมื่อ Pipeline ทำงานได้แล้ว คุณสามารถ:

1. **เพิ่ม Stages ใหม่** เช่น deployment, integration tests
2. **ตั้งค่า Webhooks** สำหรับ auto-trigger จาก Git
3. **สร้าง Multi-branch Pipeline** สำหรับ development branches
4. **เพิ่ม Security scanning** และ compliance checks
5. **ตั้งค่า Monitoring** และ alerting ที่ละเอียดขึ้น

Pipeline นี้เป็นจุดเริ่มต้นที่ดีสำหรับ CI/CD ใน Data Engineering!
