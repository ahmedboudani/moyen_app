# نظام إدارة التلاميذ

تطبيق ويب لإدارة بيانات التلاميذ وعلاماتهم في المؤسسات التعليمية.

## المميزات

- إدارة الأقسام والفصول الدراسية
- تسجيل بيانات التلاميذ
- إدخال وحساب العلامات
- عرض النتائج والإحصائيات
- تصدير التقارير بصيغة PDF
- استيراد بيانات التلاميذ من ملفات Excel

## المتطلبات

- Python 3.9+
- قاعدة بيانات SQLite

## التثبيت

1. استنساخ المستودع:
   ```bash
   git clone https://github.com/username/moyyen.git
   cd moyyen
   ```

2. إنشاء بيئة افتراضية:
   ```bash
   python -m venv venv
   source venv/bin/activate  # على Windows: venv\Scripts\activate
   ```

3. تثبيت المكتبات المطلوبة:
   ```bash
   pip install -r requirements.txt
   ```

4. تهيئة قاعدة البيانات:
   ```bash
   python -c "from app import app; from models import db; app.app_context().push(); db.create_all()"
   ```

## التشغيل

```bash
python app.py
```

ثم افتح المتصفح على العنوان: http://localhost:5000

## النشر على Heroku

1. تثبيت Heroku CLI وإنشاء حساب على Heroku
2. تسجيل الدخول إلى Heroku:
   ```bash
   heroku login
   ```
3. إنشاء تطبيق جديد:
   ```bash
   heroku create your-app-name
   ```
4. إضافة قاعدة بيانات PostgreSQL:
   ```bash
   heroku addons:create heroku-postgresql:hobby-dev
   ```
5. تعيين متغيرات البيئة:
   ```bash
   heroku config:set FLASK_APP=app.py
   heroku config:set FLASK_ENV=production
   ```
6. رفع الكود إلى Heroku:
   ```bash
   git add .
   git commit -m "Initial commit"
   git push heroku main
   ```

## المؤلف

[اسمك]

## الرخصة

MIT License
