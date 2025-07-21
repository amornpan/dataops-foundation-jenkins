# คู่มือการติดตั้งและใช้งาน Jenkins Pipeline สำหรับโปรเจค ETL

## 📋 สารบัญ
1. [ข้อกำหนดเบื้องต้น](#ข้อกำหนดเบื้องต้น)
2. [การติดตั้ง Jenkins](#การติดตั้ง-jenkins)
3. [การตั้งค่า Jenkins เบื้องต้น](#การตั้งค่า-jenkins-เบื้องต้น)
4. [การเตรียม Git Repository](#การเตรียม-git-repository)
5. [การสร้าง Pipeline Job](#การสร้าง-pipeline-job)
6. [การตั้งค่า Credentials](#การตั้งค่า-credentials)
7. [การรัน Pipeline ครั้งแรก](#การรัน-pipeline-ครั้งแรก)
8. [การติดตาม และแก้ไขปัญหา](#การติดตาม-และแก้ไขปัญหา)
9. [การใช้งานประจำวัน](#การใช้งานประจำวัน)
10. [Tips และ Best Practices](#tips-และ-best-practices)

---

## 🎯 ข้อกำหนดเบื้องต้น

### Software Requirements
- **Java 11 หรือใหม่กว่า** (สำหรับ Jenkins)
- **Docker** (วิธีติดตั้งแนะนำ)
- **Git** (สำหรับ version control)
- **Python 3.9+** (บน Jenkins server)
- **Access ถึง SQL Server** (mssql.minddatatech.com)

### Hardware Requirements
- **RAM**: อย่างน้อย 4GB (แนะนำ 8GB+)
- **Storage**: อย่างน้อย 10GB ว่าง
- **CPU**: 2 cores ขึ้นไป

### Network Requirements
- Internet access สำหรับดาวน์โหลด plugins
- Access ถึง GitHub repository
- Access ถึง SQL Server (mssql.minddatatech.com:1433)

---

## 🚀 การติดตั้ง Jenkins

### วิธีที่ 1: ติดตั้งด้วย Docker (แนะนำ)

#### Step 1: ติดตั้ง Docker
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install docker.io docker-compose
sudo usermod -aG docker $USER

# CentOS/RHEL
sudo yum install docker docker-compose
sudo systemctl start docker
sudo systemctl enable docker
```

#### Step 2: สร้าง Docker Compose File
```yaml
# สร้างไฟล์ docker-compose.yml
version: '3.8'
services:
  jenkins:
    image: jenkins/jenkins:lts
    container_name: jenkins-etl
    ports:
      - "8080:8080"
      - "50000:50000"
    volumes:
      - jenkins_home:/var/jenkins_home
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      - JAVA_OPTS=-Djenkins.install.runSetupWizard=false
    restart: unless-stopped

volumes:
  jenkins_home:
```

#### Step 3: รัน Jenkins
```bash
# รัน Jenkins
docker-compose up -d

# ตรวจสอบสถานะ
docker-compose ps

# ดู logs
docker-compose logs -f jenkins
```

#### Step 4: เข้าถึง Jenkins
- เปิดเบราว์เซอร์ไปที่: `http://localhost:8080`
- รอ Jenkins เริ่มต้น (ประมาณ 2-3 นาที)

### วิธีที่ 2: ติดตั้งแบบ Native (Ubuntu)

```bash
# อัปเดต system
sudo apt update

# ติดตั้ง Java
sudo apt install openjdk-11-jdk

# เพิ่ม Jenkins repository
curl -fsSL https://pkg.jenkins.io/debian/jenkins.io.key | sudo tee \
  /usr/share/keyrings/jenkins-keyring.asc > /dev/null

echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] \
  https://pkg.jenkins.io/debian binary/ | sudo tee \
  /etc/apt/sources.list.d/jenkins.list > /dev/null

# ติดตั้ง Jenkins
sudo apt update
sudo apt install jenkins

# เริ่มและเปิดใช้งาน Jenkins
sudo systemctl start jenkins
sudo systemctl enable jenkins

# ตรวจสอบสถานะ
sudo systemctl status jenkins
```

---

## ⚙️ การตั้งค่า Jenkins เบื้องต้น

### Step 1: Jenkins Initial Setup

#### 1.1 รับ Initial Admin Password
```bash
# สำหรับ Docker
docker exec jenkins-etl cat /var/jenkins_home/secrets/initialAdminPassword

# สำหรับ Native install
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
```

#### 1.2 ปลดล็อค Jenkins
1. เปิดเบราว์เซอร์ไปที่ `http://localhost:8080`
2. ใส่ Initial Admin Password
3. คลิก **Continue**

#### 1.3 ติดตั้ง Plugins
1. เลือก **Install suggested plugins**
2. รอให้ plugins ติดตั้งเสร็จ (5-10 นาที)

#### 1.4 สร้าง Admin User
1. กรอกข้อมูล Admin User:
   - **Username**: `admin`
   - **Password**: `admin123` (หรือรหัสผ่านที่ต้องการ)
   - **Full name**: `Jenkins Administrator`
   - **E-mail**: `admin@yourcompany.com`
2. คลิก **Save and Continue**

#### 1.5 ตั้งค่า Jenkins URL
1. ตรวจสอบ Jenkins URL: `http://localhost:8080/`
2. คลิก **Save and Finish**
3. คลิก **Start using Jenkins**

### Step 2: ติดตั้ง Additional Plugins

#### 2.1 เข้าไปที่ Plugin Manager
1. **Jenkins Dashboard** → **Manage Jenkins** → **Manage Plugins**
2. คลิกแท็บ **Available**

#### 2.2 ติดตั้ง Required Plugins
ค้นหาและติดตั้ง plugins เหล่านี้:

**Essential Plugins:**
- ✅ **Pipeline Plugin** (มักติดตั้งแล้ว)
- ✅ **Git Plugin** (มักติดตั้งแล้ว)
- ✅ **Credentials Plugin** (มักติดตั้งแล้ว)

**Additional Plugins:**
- ✅ **Blue Ocean** (สำหรับ UI ที่สวยกว่า)
- ✅ **HTML Publisher Plugin** (สำหรับ reports)
- ✅ **JUnit Plugin** (สำหรับ test results)
- ✅ **Workspace Cleanup Plugin**
- ✅ **Timestamper Plugin**
- ✅ **AnsiColor Plugin**
- ✅ **Email Extension Plugin**

#### 2.3 ติดตั้งและ Restart
1. เลือก plugins ที่ต้องการ
2. คลิก **Install without restart**
3. รอให้ติดตั้งเสร็จ
4. คลิก **Restart Jenkins when installation is complete**

---

## 📁 การเตรียม Git Repository

### Step 1: Clone โปรเจค

```bash
# Clone โปรเจค ETL
git clone https://github.com/amornpan/dataops-foundation-jenkins.git
cd dataops-foundation-jenkins

# ตรวจสอบไฟล์สำคัญ
ls -la
```

**ไฟล์สำคัญที่ต้องมี:**
- ✅ `Jenkinsfile` - Pipeline definition
- ✅ `etl_main.py` - ETL script หลัก
- ✅ `requirements.txt` - Python dependencies
- ✅ `jenkins_test.py` - Test script สำหรับ Jenkins
- ✅ `simple_test.py` - Simple test script
- ✅ `data/README.md` - Data folder placeholder

### Step 2: ตรวจสอบ Jenkinsfile

```bash
# ดู Jenkinsfile
cat Jenkinsfile
```

**Jenkinsfile ต้องมีโครงสร้างแบบนี้:**
```groovy
pipeline {
    agent any
    
    environment {
        // Database configuration
        DB_SERVER = 'mssql.minddatatech.com'
        DB_NAME = 'TestDB'
        DB_USERNAME = 'SA'
        DB_PASSWORD = credentials('mssql-password')
        // ... other config
    }
    
    stages {
        stage('🔄 Checkout') { ... }
        stage('🐍 Setup Python Environment') { ... }
        stage('🔍 Code Quality Checks') { ... }
        stage('📊 Data Quality Validation') { ... }
        stage('🧪 Unit Tests') { ... }
        stage('🔌 Database Connection Test') { ... }
        stage('🏗️ ETL Dry Run') { ... }
    }
    
    post { ... }
}
```

### Step 3: ทดสอบโปรเจคใน Local (Optional)

```bash
# สร้าง virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# หรือ venv\Scripts\activate  # Windows

# ติดตั้ง dependencies
pip install -r requirements.txt

# ทดสอบ
python jenkins_test.py
```

---

## 🛠️ การสร้าง Pipeline Job

### Step 1: สร้าง New Item

#### 1.1 เข้าสู่ Jenkins Dashboard
1. เปิดเบราว์เซอร์ไปที่ `http://localhost:8080`
2. Login ด้วย admin credentials

#### 1.2 สร้าง New Job
1. คลิก **New Item** ที่มุมซ้ายบน
2. กรอก **Item name**: `etl-ci-pipeline`
3. เลือก **Pipeline**
4. คลิก **OK**

### Step 2: กำหนดค่า Pipeline Job

#### 2.1 General Settings
ในหน้า Configuration:

**General Section:**
- ✅ **Description**: `ETL Pipeline สำหรับประมวลผล Loan Data และสร้าง Star Schema`

**Build Triggers:**
- ✅ **GitHub hook trigger for GITScm polling** (ถ้าใช้ GitHub webhooks)
- ✅ **Poll SCM**: `H/5 * * * *` (ตรวจสอบทุก 5 นาที)

**Advanced Project Options:**
- ✅ **Discard old builds**
  - **Days to keep builds**: `30`
  - **Max # of builds to keep**: `20`

#### 2.2 Pipeline Configuration

**Pipeline Section:**
- **Definition**: `Pipeline script from SCM`
- **SCM**: `Git`
- **Repository URL**: `https://github.com/amornpan/dataops-foundation-jenkins.git`
- **Credentials**: (ตั้งค่าในขั้นตอนถัดไป)
- **Branches to build**: `*/main`
- **Script Path**: `Jenkinsfile`

**Additional Behaviours:**
- ✅ **Lightweight checkout** (เพื่อความเร็ว)

#### 2.3 Save Configuration
คลิก **Save** เพื่อบันทึกการตั้งค่า

---

## 🔐 การตั้งค่า Credentials

### Step 1: สร้าง Database Credential

#### 1.1 เข้าไปที่ Credentials Management
1. **Jenkins Dashboard** → **Manage Jenkins** → **Manage Credentials**
2. คลิก **Global credentials (unrestricted)**
3. คลิก **Add Credentials**

#### 1.2 สร้าง SQL Server Password
กรอกข้อมูล:
- **Kind**: `Secret text`
- **Scope**: `Global (Jenkins, nodes, items, all child items, etc)`
- **Secret**: `Passw0rd123456`
- **ID**: `mssql-password`
- **Description**: `SQL Server Password for ETL Pipeline`

คลิก **OK**

### Step 2: สร้าง Git Credentials (ถ้าใช้ Private Repository)

#### 2.1 GitHub Personal Access Token
1. ไปที่ GitHub → **Settings** → **Developer settings** → **Personal access tokens**
2. คลิก **Generate new token**
3. เลือก scopes:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `admin:repo_hook` (Admin repo hooks)
4. คลิก **Generate token**
5. **Copy token** ทันที (จะดูได้ครั้งเดียว)

#### 2.2 เพิ่ม Git Credentials ใน Jenkins
1. กลับไปที่ **Manage Credentials**
2. คลิก **Add Credentials**
3. กรอกข้อมูล:
   - **Kind**: `Username with password`
   - **Scope**: `Global`
   - **Username**: `GitHub username ของคุณ`
   - **Password**: `Personal Access Token ที่ copy มา`
   - **ID**: `github-credentials`
   - **Description**: `GitHub Access for ETL Repository`
4. คลิก **OK**

### Step 3: อัปเดต Pipeline Job ให้ใช้ Credentials

1. กลับไปที่ pipeline job `etl-ci-pipeline`
2. คลิก **Configure**
3. ในส่วน **Pipeline** → **Repository URL**
4. เลือก **Credentials**: `github-credentials`
5. คลิก **Save**

---

## ▶️ การรัน Pipeline ครั้งแรก

### Step 1: รัน Build แรก

#### 1.1 Manual Build
1. ไปที่ pipeline job `etl-ci-pipeline`
2. คลิก **Build Now**
3. ดูการทำงานใน **Build History**

#### 1.2 ตรวจสอบ Console Output
1. คลิกที่ build number (เช่น `#1`)
2. คลิก **Console Output**
3. ดูการทำงานแบบ real-time

### Step 2: เข้าใจ Pipeline Stages

Pipeline จะทำงานตามลำดับนี้:

#### Stage 1: 🔄 Checkout
```
=== ETL CI Pipeline Started ===
Build: 1
Branch: main
✅ ETL script found
```

#### Stage 2: 🐍 Setup Python Environment
```
Setting up Python environment...
✅ Core packages installed
```

#### Stage 3: 🔍 Code Quality Checks
```
Parallel execution:
- Linting (flake8)
- Code Formatting (black)
⚠️ Code formatting issues found
```

#### Stage 4: 📊 Data Quality Validation
```
=== Data Quality Report ===
⚠️ Data file not found: data/LoanStats_web_small.csv
Skipping data quality validation...
```

#### Stage 5: 🧪 Unit Tests
```
Running jenkins_test.py...
✅ Core packages imported successfully
✅ ETL function test passed: 144 columns
```

#### Stage 6: 🔌 Database Connection Test
```
=== Database Connection Test ===
⚠️ Database connection failed: [connection details]
Note: This is expected if running in CI
```

#### Stage 7: 🏗️ ETL Dry Run
```
=== ETL Dry Run ===
✅ ETL functions tested: 144 columns analyzed
✅ Dry run completed successfully
```

### Step 3: ตรวจสอบผลลัพธ์

#### 3.1 Build สำเร็จ (สีเขียว)
```
=== Pipeline Completed ===
Build Number: 1
Duration: 2 min 34 sec
🎉 CI Pipeline succeeded! Ready for deployment.
```

#### 3.2 Build ล้มเหลว (สีแดง)
```
❌ CI Pipeline failed!
```
→ ดู Console Output เพื่อหาสาเหตุ

#### 3.3 Build ไม่เสถียร (สีเหลือง)
```
⚠️ CI Pipeline unstable - some tests may have failed
```
→ บางส่วนผ่าน บางส่วนล้มเหลว

---

## 🔍 การติดตาม และแก้ไขปัญหา

### ปัญหาที่พบบ่อยและวิธีแก้ไข

#### 1. **Error: mssql-password credential not found**

**สาเหตุ**: ยังไม่ได้สร้าง credential

**วิธีแก้:**
```bash
1. Manage Jenkins → Manage Credentials
2. Add Credentials → Secret text
3. ID: mssql-password
4. Secret: Passw0rd123456
```

#### 2. **Error: Permission denied (pip install)**

**สาเหตุ**: Jenkins ไม่มีสิทธิ์ติดตั้ง packages

**วิธีแก้:**
```bash
# ในเซิร์ฟเวอร์ Jenkins
sudo chown -R jenkins:jenkins /var/jenkins_home
sudo chmod +x /usr/bin/python3
```

#### 3. **Error: Data file not found**

**สาเหตุ**: ไฟล์ข้อมูลไม่ได้อยู่ใน repository

**วิธีแก้:**
- นี่เป็นเรื่องปกติ เพราะไฟล์ข้อมูลไม่ควรอยู่ใน Git
- Pipeline จะ skip ขั้นตอนที่ต้องใช้ไฟล์ข้อมูล
- สำหรับ production ให้วางไฟล์ข้อมูลใน Jenkins workspace

#### 4. **Error: Database connection failed**

**สาเหตุ**: Jenkins server เชื่อมต่อ database ไม่ได้

**วิธีแก้:**
```bash
# ตรวจสอบ network connectivity
ping mssql.minddatatech.com
telnet mssql.minddatatech.com 1433

# ตรวจสอบ firewall
sudo ufw status
```

#### 5. **Error: Python module not found**

**สาเหตุ**: Virtual environment ไม่ถูกสร้างถูกต้อง

**วิธีแก้:**
```bash
# ใน Jenkinsfile, เพิ่มการ debug
sh '''
    . ${VIRTUAL_ENV}/bin/activate
    which python
    pip list
    python -c "import sys; print(sys.path)"
'''
```

### การ Debug แบบละเอียด

#### 1. เปิด Debug Mode
เพิ่มใน Jenkinsfile:
```groovy
environment {
    JENKINS_DEBUG = 'true'
}
```

#### 2. ตรวจสอบ Workspace
```groovy
sh '''
    pwd
    ls -la
    echo "Python version: $(python3 --version)"
    echo "Pip version: $(pip3 --version)"
'''
```

#### 3. ตรวจสอบ Environment Variables
```groovy
sh '''
    env | grep -E "(DB_|PYTHON_|VIRTUAL_)"
'''
```

### Log Files และ Monitoring

#### 1. Jenkins System Logs
```bash
# Docker
docker logs jenkins-etl

# Native
sudo tail -f /var/log/jenkins/jenkins.log
```

#### 2. Build Logs
- **Jenkins Dashboard** → **Build History** → **Console Output**

#### 3. Workspace Inspection
```bash
# เข้าไปดู workspace ของ job
sudo ls -la /var/jenkins_home/workspace/etl-ci-pipeline/
```

---

## 📅 การใช้งานประจำวัน

### การรัน Pipeline

#### 1. Manual Build
```
Jenkins Dashboard → etl-ci-pipeline → Build Now
```

#### 2. Build with Parameters (ถ้ามี)
```
Jenkins Dashboard → etl-ci-pipeline → Build with Parameters
- Environment: DEV/STAGING/PROD
- Skip Tests: true/false
- Dry Run: true/false
```

#### 3. Scheduled Build
Pipeline จะรันอัตโนมัติตาม schedule ใน Jenkinsfile:
```groovy
triggers {
    cron('0 2 * * *')  // ทุกวันเวลา 2:00 AM
}
```

### การตรวจสอบสถานะ

#### 1. Dashboard Overview
- **Green**: Build สำเร็จ
- **Red**: Build ล้มเหลว  
- **Yellow**: Build ไม่เสถียร
- **Gray**: ยังไม่ได้รัน หรือถูกยกเลิก

#### 2. Build History
```
etl-ci-pipeline → Build History
- ดูประวัติ builds ทั้งหมด
- เปรียบเทียบ builds ต่างๆ
- ดู trends และ patterns
```

#### 3. Blue Ocean View (แนะนำ)
```
Jenkins Dashboard → Open Blue Ocean
- UI ที่สวยกว่า
- ดู pipeline visualization
- ง่ายต่อการ debug
```

### การจัดการ Builds

#### 1. การยกเลิก Build
```
Build History → [Build Number] → Stop Build
```

#### 2. การลบ Build เก่า
```
Build History → [Build Number] → Delete Build
```

#### 3. การ Rebuild
```
Build History → [Build Number] → Rebuild
```

### Notifications และ Alerts

#### 1. Email Notifications
Pipeline จะส่ง email เมื่อ:
- ✅ Build สำเร็จ
- ❌ Build ล้มเหลว
- ⚠️ Build กลับมาเป็นปกติ

#### 2. Slack Notifications (ถ้าตั้งค่าไว้)
```
#data-engineering channel:
✅ ETL Pipeline Success - Build #5
❌ ETL Pipeline Failed - Build #6
```

---

## 💡 Tips และ Best Practices

### Security Best Practices

#### 1. Credential Management
```
❌ อย่าเก็บ passwords ใน code
✅ ใช้ Jenkins Credentials เท่านั้น
✅ ใช้ least privilege principle
✅ หมุนเวียน passwords เป็นประจำ
```

#### 2. Access Control
```
✅ สร้าง user roles ที่เหมาะสม
✅ จำกัด access ต่อ sensitive jobs
✅ Enable audit logging
✅ ใช้ 2FA ถ้าเป็นไปได้
```

### Performance Optimization

#### 1. Pipeline Efficiency
```groovy
// ใช้ parallel stages
parallel {
    stage('Test 1') { ... }
    stage('Test 2') { ... }
}

// Clean workspace หลัง build
cleanWs()

// ใช้ appropriate timeouts
timeout(time: 30, unit: 'MINUTES')
```

#### 2. Resource Management
```
✅ จำกัด concurrent builds
✅ ใช้ node labels สำหรับ specific tasks
✅ Monitor disk space และ memory
✅ Archive artifacts ที่จำเป็นเท่านั้น
```

### Maintenance Tasks

#### 1. Weekly Tasks
- [ ] ตรวจสอบ build success rate
- [ ] ลบ builds เก่าที่ไม่จำเป็น
- [ ] ตรวจสอบ disk space
- [ ] Review failed builds

#### 2. Monthly Tasks
- [ ] อัปเดต Jenkins และ plugins
- [ ] Backup Jenkins configuration
- [ ] Review และอัปเดต credentials
- [ ] ตรวจสอบ security logs

#### 3. Backup และ Recovery
```bash
# Backup Jenkins home
docker exec jenkins-etl tar -czf /var/jenkins_home/backup.tar.gz /var/jenkins_home

# Copy backup ออกมา
docker cp jenkins-etl:/var/jenkins_home/backup.tar.gz ./jenkins-backup.tar.gz
```

### ปรับแต่ง Pipeline สำหรับ Production

#### 1. เพิ่ม Environments
```groovy
parameters {
    choice(
        name: 'ENVIRONMENT',
        choices: ['DEV', 'STAGING', 'PROD'],
        description: 'Target deployment environment'
    )
}
```

#### 2. เพิ่ม Approval Steps
```groovy
stage('Deploy to Production') {
    when {
        expression { params.ENVIRONMENT == 'PROD' }
    }
    steps {
        input message: 'Deploy to Production?', ok: 'Deploy'
        // deployment steps
    }
}
```

#### 3. เพิ่ม Monitoring
```groovy
post {
    always {
        // Archive test results
        publishTestResults testResultsPattern: 'test-results.xml'
        
        // Publish coverage reports
        publishHTML([
            allowMissing: false,
            alwaysLinkToLastBuild: true,
            keepAll: true,
            reportDir: 'htmlcov',
            reportFiles: 'index.html',
            reportName: 'Coverage Report'
        ])
    }
}
```

### Troubleshooting Checklist

เมื่อ Pipeline ล้มเหลว ให้ตรวจสอบตามลำดับ:

#### 1. Basic Checks
- [ ] Console output มี error message อะไรบ้าง?
- [ ] Credentials ถูกต้องหรือไม่?
- [ ] Network connectivity เป็นอย่างไร?
- [ ] Disk space เหลือเพียงพอหรือไม่?

#### 2. Environment Checks
- [ ] Python version ถูกต้องหรือไม่?
- [ ] Virtual environment สร้างสำเร็จหรือไม่?
- [ ] Dependencies ติดตั้งครบหรือไม่?

#### 3. Code Checks
- [ ] Jenkinsfile syntax ถูกต้องหรือไม่?
- [ ] Python code มี syntax error หรือไม่?
- [ ] Import statements ถูกต้องหรือไม่?

#### 4. External Dependencies
- [ ] Git repository accessible หรือไม่?
- [ ] Database connection ทำงานหรือไม่?
- [ ] Required services running หรือไม่?

---

## 🎉 สรุป

คุณได้เรียนรู้การติดตั้งและใช้งาน Jenkins Pipeline สำหรับโปรเจค ETL แล้ว โดยครอบคลุม:

✅ **การติดตั้ง Jenkins** แบบ Docker และ Native  
✅ **การตั้งค่าเบื้องต้น** และ plugin management  
✅ **การสร้าง Pipeline Job** และ configuration  
✅ **การจัดการ Credentials** อย่างปลอดภัย  
✅ **การรัน Pipeline** และการติดตามผลลัพธ์  
✅ **การแก้ไขปัญหา** ที่พบบ่อย  
✅ **Best practices** สำหรับการใช้งานจริง  

Pipeline นี้จะช่วยให้คุณ:
- **Automate ETL process** ลดการทำงานด้วยมือ
- **Ensure code quality** ด้วย automated testing
- **Deploy safely** ด้วย staging environments
- **Monitor and alert** เมื่อมีปัญหา

**Happy CI/CD! 🚀**

---

## 📞 ติดต่อและสนับสนุน

หากมีปัญหาหรือข้อสงสัย:
1. ตรวจสอบ Console Output ใน Jenkins
2. ดู troubleshooting section ในคู่มือนี้  
3. ตรวจสอบ Jenkins logs
4. หาข้อมูลเพิ่มเติมใน [Jenkins Documentation](https://www.jenkins.io/doc/)
   
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
