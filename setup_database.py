"""
هذا الملف يستخدم لتهيئة قاعدة البيانات وتنفيذ الأوامر SQL الأولية
"""

import os
import sys
from flask import Flask
from models import db, User, Class, Student, Grade, GeneralInfo
from config import Config

def create_app():
    """
    إنشاء تطبيق Flask للتهيئة
    """
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app

def init_database():
    """
    تهيئة قاعدة البيانات وإنشاء الجداول
    """
    app = create_app()

    with app.app_context():
        # التحقق مما إذا كنا نستخدم Supabase
        is_supabase = 'supabase' in app.config.get('SQLALCHEMY_DATABASE_URI', '').lower()

        if is_supabase:
            print("تم اكتشاف قاعدة بيانات Supabase.")
            print("يرجى تشغيل init_supabase.py لتهيئة قاعدة البيانات.")
            return

        # إنشاء الجداول لقاعدة البيانات المحلية
        print("إنشاء جداول قاعدة البيانات المحلية...")
        db.create_all()
        print("تم إنشاء الجداول بنجاح!")

if __name__ == "__main__":
    try:
        init_database()
    except Exception as e:
        print(f"حدث خطأ أثناء تهيئة قاعدة البيانات: {e}")
        sys.exit(1)
