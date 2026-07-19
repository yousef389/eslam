# نظام ERP للأدوات الصحية

نظام متكامل لإدارة محل الأدوات الصحية يدعم:
- إدارة المنتجات والمخزون
- إدارة العملاء والموردين
- المبيعات والمشتريات
- حسابات العملاء والموردين (ذمم)
- الصندوق والإيرادات والمصروفات
- التقارير المالية
- تحليل الفواتير بالذكاء الاصطناعي
- بوت تلجرام للتحليل

## التقنيات
- **Backend**: Python, FastAPI, SQLAlchemy, PostgreSQL
- **Frontend**: React, TypeScript, Tailwind CSS
- **AI**: Google Gemini
- **Bot**: python-telegram-bot

## التشغيل

### محلياً
```bash
# قاعدة البيانات
docker run -d --name erp_db -p 5432:5432 -e POSTGRES_DB=sanitary_erp -e POSTGRES_USER=erp_admin -e POSTGRES_PASSWORD=secure_password_123 postgres:16-alpine
docker run -d --name erp_redis -p 6379:6379 redis:7-alpine

# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

### بيانات الدخول
- اسم المستخدم: `admin`
- كلمة المرور: `admin123`
