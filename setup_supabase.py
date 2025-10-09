"""
هذا الملف يستخدم لتهيئة قاعدة بيانات Supabase وتنفيذ الأوامر SQL الأولية
"""

# SQL لإنشاء الجداول المطلوبة
CREATE_USER_TABLE = """
CREATE TABLE IF NOT EXISTS "user" (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
"""

CREATE_GENERAL_INFO_TABLE = """
CREATE TABLE IF NOT EXISTS general_info (
    id SERIAL PRIMARY KEY,
    institution VARCHAR(200) NOT NULL,
    directorate VARCHAR(200) NOT NULL,
    teacher VARCHAR(100) NOT NULL,
    subject VARCHAR(100) NOT NULL,
    user_id INTEGER REFERENCES "user"(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
"""

CREATE_CLASS_TABLE = """
CREATE TABLE IF NOT EXISTS class (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    user_id INTEGER REFERENCES "user"(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
"""

CREATE_STUDENT_TABLE = """
CREATE TABLE IF NOT EXISTS student (
    id SERIAL PRIMARY KEY,
    fullname VARCHAR(100) NOT NULL,
    semester VARCHAR(20) NOT NULL,
    class_id INTEGER REFERENCES class(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES "user"(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
"""

CREATE_GRADE_TABLE = """
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
"""

# قائمة بجميع أوامر SQL التي سيتم تنفيذها
ALL_TABLES_SQL = [
    CREATE_USER_TABLE,
    CREATE_GENERAL_INFO_TABLE,
    CREATE_CLASS_TABLE,
    CREATE_STUDENT_TABLE,
    CREATE_GRADE_TABLE
]

def setup_supabase():
    """
    هذه الدالة تطبع أوامر SQL التي يجب تنفيذها في Supabase
    """
    print("=== أوامر SQL لتهيئة قاعدة بيانات Supabase ===")
    print("

")
    print("1. انتقل إلى لوحة تحكم Supabase")
    print("2. اذهب إلى قسم SQL Editor")
    print("3. انسخ والصق الأوامر التالية:")
    print("
")

    for sql in ALL_TABLES_SQL:
        print(sql)
        print("
")

    print("============================================")
    print("
")
    print("بعد تنفيذ هذه الأوامر، تأكد من إضافة متغيرات البيئة التالية في منصة النشر:")
    print("- DATABASE_URL: رابط اتصال قاعدة البيانات من Supabase")
    print("- SUPABASE_URL: رابط مشروع Supabase")
    print("- SUPABASE_KEY: مفتاح API العام (anon key) من Supabase")

if __name__ == "__main__":
    setup_supabase()
