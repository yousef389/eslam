# نظام ERP للأدوات الصحية

نظام متكامل لإدارة محلات الأدوات الصحية والمعدات الإنشائية.

## المميزات

- إدارة المنتجات والمخزون
- إدارة العملاء والموردين
- نظام المبيعات والمشتريات
- نظام الحسابات والديون
- إدارة الصندوق
- تقارير مالية
- ذكاء اصطناعي لتحليل الفواتير
- بوت تيليجرام
- إعدادات النظام

## التقنيات

### Backend
- Python 3.12
- FastAPI
- SQLAlchemy 2.0 (Async)
- PostgreSQL 16
- Redis
- JWT Authentication

### Frontend
- React 18
- TypeScript
- Vite
- Tailwind CSS
- React Query

## التشغيل المحلي

### متطلبات
- Python 3.12+
- Node.js 18+
- PostgreSQL 16
- Redis

### 1. إعداد قاعدة البيانات

```bash
# إنشاء قاعدة البيانات
createdb -U postgres sanitary_erp
```

### 2. إعداد الباك اند

```bash
cd backend

# إنشاء بيئة افتراضية
python -m venv venv
source venv/bin/activate

# تثبيت المتطلبات
pip install -r requirements.txt

# إنشاء ملف .env
cp ../.env.example .env
# عدّل .env بإعدادات قاعدة البيانات

# تشغيل الباك اند
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. إعداد الفرونت

```bash
cd frontend

# تثبيت المتطلبات
npm install

# تشغيل الفرونت
npm run dev
```

### 4. إعداد قاعدة البيانات

```bash
cd backend

# إنشاء الجداول
python -c "from app.core.events import create_tables; import asyncio; asyncio.run(create_tables())"

# إنشاء مستخدم admin
python -c "from app.core.events import seed_admin_user; import asyncio; asyncio.run(seed_admin_user())"

# إنشاء الإعدادات الافتراضية
python -c "from app.core.events import seed_default_settings; import asyncio; asyncio.run(seed_default_settings())"
```

## بيانات الدخول الافتراضية

- **اسم المستخدم:** admin
- **كلمة المرور:** Admin@12345

## API Documentation

بعد تشغيل الباك اند، يمكنك الوصول لـ Swagger UI على:
```
http://localhost:8000/docs
```

## روابط مفيدة

- [دليل التثبيت](INSTALL.md)
- [دليل النشر](DEPLOYMENT.md)
