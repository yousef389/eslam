# دليل النشر على InfinityFree + Render.com (مجاني بالكامل)

## النظرة العامة

النظام يتكون من جزأين:
1. **Backend** (Python FastAPI) → يُنشر على **Render.com** (مجاني)
2. **Frontend** (React Static Files) → يُنشر على **InfinityFree** (مجاني)
3. **PHP Bridge** → يربط الفرونت بالباك اند

```
المستخدم → InfinityFree (static files + PHP proxy) → Render.com (API + Database)
```

---

## الخطوة 1: نشر Backend على Render.com

### 1.1 إعداد قاعدة البيانات

1. أنشئ حساب على [Render.com](https://render.com)
2. اذهب إلى **New > PostgreSQL**
3. اختر **Free** plan
4. احفظ الـ connection string

### 1.2 إعداد Backend

1. اذهب إلى **New > Web Service**
2. اربط حسابك بـ GitHub
3. اختر مستودع `eslam`
4. أعدّل الإعدادات:

```
Build Command: cd backend && pip install -r requirements.txt
Start Command: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
```

5. Environment Variables:

```
DATABASE_URL=<your-postgres-url-from-render>
JWT_SECRET_KEY=<generate-a-strong-key>
DEBUG=false
PYTHON_VERSION=3.12
```

ولّد مفتاح JWT:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(64))"
```

6. اضغط **Create Web Service**
7. انتظر حتى يكتمل البناء
8. انسخ الـ URL (مثلاً: `https://sanitary-erp.onrender.com`)

### 1.3 اختبار Backend

```bash
curl https://your-app.onrender.com/health
# يجب أن يُرجع: {"status":"healthy"}
```

---

## الخطوة 2: بناء Frontend

### 2.1 تعديل API URL

عدّل ملف `frontend/.env.production`:

```
VITE_API_URL=https://your-app.onrender.com/api/v1
```

### 2.2 بناء الفرونت

```bash
cd frontend
npm install
npm run build
```

الملفات المبنية ستكون في `frontend/dist/`

---

## الخطوة 3: رفع الملفات على InfinityFree

### 3.1 رفع PHP Bridge

1. افتح **File Manager** في لوحة تحكم InfinityFree
2. اذهب إلى مجلد `htdocs`
3. ارفع الملفات التالية:
   - `index.php` (من `deploy/php-bridge/`)
   - `.htaccess` (من `deploy/php-bridge/`)

### 3.2 تعديل API URL في PHP Bridge

افتح `index.php` وعدّل السطر:

```php
$API_BASE_URL = 'https://your-app.onrender.com'; // <-- غيّر هذا
```

### 3.3 رفع ملفات Frontend

1. ارفع **محتويات** مجلد `frontend/dist/*` إلى مجلد `htdocs`
2. تأكد أن `index.html` موجود في `htdocs/index.html`

### 3.4 هيكل الملفات النهائية

```
htdocs/
├── index.php          (PHP Bridge)
├── .htaccess          (URL rewriting)
├── index.html         (React app entry)
├── assets/
│   ├── index-xxxxx.js
│   └── index-xxxxx.css
└── ... (باقي ملفات dist)
```

---

## الخطوة 4: اختبار النظام

1. افتح `http://eslam.gt.tc`
2. يجب أن تظهر صفحة الدخول
3. سجّل الدخول بـ: `admin` / `Admin@12345`

---

## ملاحظات مهمة

### DNS
قد يستغرق حتى 72 ساعة حتى يعمل النطاق. جرّب:
- `http://eslam.gt.tc` مباشرة
- `http://if0_42446288.infinityfree.com` كعنوان بديل

### Render.com Free Tier
- الخادم ي.Sleep بعد 15 دقيقة من عدم الاستخدام
- أول طلب بعد الـ Sleep يستغرق ~30 ثانية
- يمكنك استخدام [UptimeRobot](https://uptimerobot.com) للحفاظ عليه مفعلاً

### تحديث Backend
عند أي تعديل على الكود:
1. ادفع التغييرات لـ GitHub
2. Render سيعيد البناء تلقائياً

### تحديث Frontend
1. أعد البناء: `npm run build`
2. ارفع الملفات الجديدة من `dist/` إلى InfinityFree

---

## استعادة كلمة المرور

```bash
# الدخول لقاعدة البيانات على Render
psql $DATABASE_URL

# تغيير كلمة مرور admin
UPDATE users SET password_hash = '$(python3 -c "from passlib.context import CryptContext; print(CryptContext(schemes=[\"bcrypt\"]).hash(\"NEW_PASSWORD\"))")' WHERE username = 'admin';
```
