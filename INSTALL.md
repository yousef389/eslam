# دليل التثبيت

## المتطلبات المسبقة

### للتطوير المحلي
- Python 3.12 أو أعلى
- Node.js 18 أو أعلى
- PostgreSQL 16
- Redis 7
- Git

### للإنتاج
- Docker و Docker Compose
- Nginx (اختياري)

## خطوات التثبيت

### 1. استنساخ المشروع

```bash
git clone https://github.com/yousef389/eslam.git
cd eslam
```

### 2. إعداد ملف البيئة

```bash
cp .env.example .env
```

عدّل ملف `.env` بالقيم المناسبة:

```ini
# قاعدة البيانات
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/sanitary_erp

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT (ولّد مفتاح جديد)
JWT_SECRET_KEY=your-secret-key-here
```

### 3. إعداد قاعدة البيانات

```bash
# إنشاء قاعدة البيانات
psql -U postgres -c "CREATE DATABASE sanitary_erp;"
psql -U postgres -c "CREATE USER erp_admin WITH PASSWORD 'your_password';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE sanitary_erp TO erp_admin;"
```

### 4. إعداد الباك اند

```bash
cd backend

# إنشاء بيئة افتراضية
python -m venv venv
source venv/bin/activate  # Linux/Mac
# أو
venv\Scripts\activate  # Windows

# تثبيت المتطلبات
pip install -r requirements.txt

# تشغيل الباك اند
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. إعداد الفرونت

```bash
cd frontend

# تثبيت المتطلبات
npm install

# تشغيل الفرونت
npm run dev
```

### 6. إعداد قاعدة البيانات (الجدول)

```bash
cd backend

# إنشاء الجداول تلقائياً
python -c "
import asyncio
from app.core.events import create_tables, seed_admin_user, seed_default_settings
asyncio.run(create_tables())
asyncio.run(seed_admin_user())
asyncio.run(seed_default_settings())
"
```

## استخدام Docker

### تشغيل خدمات قاعدة البيانات فقط

```bash
docker compose -f docker-compose.dev.yml up -d
```

### تشغيل المشروع كاملاً

```bash
# إعداد ملف .env
cp .env.example .env
# عدّل .env

# تشغيل
docker compose up -d
```

## التحقق من التشغيل

1. الباك اند: http://localhost:8000/docs
2. الفرونت: http://localhost:5173
3. بيانات الدخول: admin / Admin@12345

## مشاكل شائعة

### قاعدة البيانات غير متاحة
- تأكد من تشغيل PostgreSQL
- تأكد من صحة بيانات الاتصال في `.env`

### Redis غير متاح
- تأكد من تشغيل Redis
- النظام يشتغل بدون Redis مع بعض المميزات محدودة

### خطأ في JWT
- تأكد من تعيين `JWT_SECRET_KEY` في `.env`
- لا تستخدم المفتاح الافتراضي في الإنتاج
