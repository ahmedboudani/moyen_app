"""
هذا الملف يستخدم لتهيئة قاعدة بيانات Supabase وتنفيذ الأوامر SQL الأولية
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

def get_db_connection():
    """
    إنشاء اتصال بقاعدة بيانات Supabase
    """
    database_url = os.environ.get('DATABASE_URL')

    if not database_url:
        raise ValueError("لم يتم تعيين متغير DATABASE_URL")

    try:
        conn = psycopg2.connect(database_url)
        return conn
    except Exception as e:
        print(f"خطأ في الاتصال بقاعدة البيانات: {e}")
        raise

def create_tables():
    """
    إنشاء الجداول المطلوبة في قاعدة بيانات Supabase
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # إنشاء جدول المستخدمين
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS "user" (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(128) NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """)

        # إنشاء جدول المعلومات العامة
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS general_info (
            id SERIAL PRIMARY KEY,
            institution VARCHAR(200) NOT NULL,
            directorate VARCHAR(200) NOT NULL,
            teacher VARCHAR(100) NOT NULL,
            subject VARCHAR(100) NOT NULL,
            user_id INTEGER REFERENCES "user"(id) ON DELETE CASCADE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """)

        # إنشاء جدول الأقسام
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS class (
            id SERIAL PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            user_id INTEGER REFERENCES "user"(id) ON DELETE CASCADE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """)

        # إنشاء جدول الطلاب
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS student (
            id SERIAL PRIMARY KEY,
            fullname VARCHAR(100) NOT NULL,
            semester VARCHAR(20) NOT NULL,
            class_id INTEGER REFERENCES class(id) ON DELETE CASCADE,
            user_id INTEGER REFERENCES "user"(id) ON DELETE CASCADE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """)

        # إنشاء جدول العلامات
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS grade (
            id SERIAL PRIMARY KEY,
            assessment DECIMAL(5,2) DEFAULT 0.0,
            test DECIMAL(5,2) DEFAULT 0.0,
            exam DECIMAL(5,2) DEFAULT 0.0,
            user_id INTEGER REFERENCES "user"(id) ON DELETE SET NULL,
            student_id INTEGER REFERENCES student(id) ON DELETE CASCADE,
            semester VARCHAR(50) NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """)

        # حفظ التغييرات
        conn.commit()
        print("تم إنشاء الجداول بنجاح!")

    except Exception as e:
        conn.rollback()
        print(f"خطأ في إنشاء الجداول: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("بدء تهيئة قاعدة بيانات Supabase...")
    create_tables()
    print("اكتملت تهيئة قاعدة البيانات!")
