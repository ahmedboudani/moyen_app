from app import app, db
from models import User

# إنشاء سياق التطبيق
with app.app_context():
    # إنشاء جميع الجداول
    db.create_all()
    print("تم إنشاء جداول قاعدة البيانات بنجاح!")
    
    # التحقق من وجود مستخدم افتراضي
    if User.query.count() == 0:
        # إنشاء مستخدم افتراضي إذا لم يكن هناك مستخدمين
        default_user = User(username="admin")
        default_user.set_password("admin")
        db.session.add(default_user)
        db.session.commit()
        print("تم إنشاء مستخدم افتراضي: admin/admin")
