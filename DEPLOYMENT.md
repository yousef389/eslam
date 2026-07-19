# دليل النشر

## النشر على VPS

### 1. تجهيز السيرفر

```bash
# تحديث النظام
sudo apt update && sudo apt upgrade -y

# تثبيت Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# تثبيت Docker Compose
sudo apt install docker-compose-plugin -y
```

### 2. نسخ المشروع

```bash
git clone https://github.com/yousef389/eslam.git
cd eslam
```

### 3. إعداد ملف البيئة

```bash
cp .env.example .env
nano .env
```

أعد تعيين القيم التالية:

```ini
DATABASE_URL=postgresql+asyncpg://erp_user:STRONG_PASSWORD@postgres:5432/sanitary_erp
JWT_SECRET_KEY=GENERATE_NEW_KEY_HERE
DB_PASSWORD=STRONG_PASSWORD
REDIS_PASSWORD=STRONG_REDIS_PASSWORD
```

ولّد مفتاح JWT جديد:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(64))"
```

### 4. تشغيل المشروع

```bash
docker compose up -d
```

### 5. إعداد Nginx (اختياري)

```bash
# تثبيت Nginx
sudo apt install nginx -y

# إعداد Proxy
sudo nano /etc/nginx/sites-available/erp
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/erp /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 6. إعداد SSL

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

## النشر على Render.com

النشر على Render يدعم **Blue Print** مباشرة عبر ملف `render.yaml`:

### النشر السريع (Blue Print)

1. اربط حسابك بـ GitHub على [Render Dashboard](https://dashboard.render.com/)
2. اضغط **New > Blueprint** واختر مستودع GitHub
3. اختر ملف `render.yaml` من المشروع
4. Render سيقوم بإنشاء:
   - **PostgreSQL Database** (مجاني)
   - **Web Service** (الباك اند + الفرونت)

### الإعداد اليدوي

#### 1. إعداد قاعدة البيانات

1. أنشئ حساب على Render.com
2. أنشئ PostgreSQL database (الخطة المجانية كافية)
3. انسخ connection string

#### 2. إعداد الباك اند + الفرونت

أنشئ **Web Service** واحد يحتوي على الباك اند والفرونت معاً:

```
Build Command: cd backend && pip install -r requirements.txt && cd ../frontend && npm install && npm run build
Start Command: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
```

**Environment Variables:**

```
DATABASE_URL=<your-postgres-url>
JWT_SECRET_KEY=<generate-a-strong-key>
DEBUG=false
PYTHON_VERSION=3.12
LOG_LEVEL=INFO
CORS_ORIGINS=["*"]
```

ولّد مفتاح JWT قوي:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(64))"
```

> **ملاحظة:** Redis اختياري - إذا لم يكن متاحاً، يستخدم النظام ذاكرة داخلية مؤقتة.
> للحصول على Redis، أضف خدمة Redis منفصلة على Render وعيّن `REDIS_URL`.

## ملاحظات أمنية مهمة

1. **لا تستخدم كلمات مرور افتراضية في الإنتاج**
2. **ولّد مفاتيح JWT قوية**
3. **فعّل HTTPS**
4. **قيّد الوصول لقاعدة البيانات**
5. **راقب السجلات بانتظام**

## النسخ الاحتياطي

```bash
# نسخ احتياطي لقاعدة البيانات
docker exec sanitary_erp_db pg_dump -U erp_admin sanitary_erp > backup_$(date +%Y%m%d).sql

# استعادة النسخ الاحتياطي
cat backup.sql | docker exec -i sanitary_erp_db psql -U erp_admin sanitary_erp
```

## المراقبة

### فحص حالة الخدمات

```bash
docker compose ps
docker compose logs api
docker compose logs postgres
```

### مراقبة الأداء

```bash
# استخدام 자원
docker stats

# سجلات الباك اند
docker compose logs -f api
```

## التحديث

```bash
# سحب أحدث التغييرات
git pull

# إعادة البناء
docker compose build

# إعادة التشغيل
docker compose up -d
```

## استعادة كلمة المرور

```bash
# الدخول لقاعدة البيانات
docker exec -it sanitary_erp_db psql -U erp_admin sanitary_erp

# تغيير كلمة مرور admin
UPDATE users SET password_hash = '$(python3 -c "from passlib.context import CryptContext; print(CryptContext(schemes=["bcrypt"]).hash("NEW_PASSWORD"))")' WHERE username = 'admin';
```
