import os
from supabase import create_client, Client
from config import Config

# إنشاء عميل Supabase
def get_supabase_client() -> Client:
    """
    إنشاء وإرجاع عميل Supabase للتفاعل مع قاعدة البيانات
    """
    url = Config.SUPABASE_URL
    key = Config.SUPABASE_KEY

    if not url or not key:
        raise ValueError("لم يتم تعيين متغيرات بيئة Supabase بشكل صحيح")

    return create_client(url, key)

# دالة مساعدة لإنشاء جداول قاعدة البيانات
def create_tables():
    """
    إنشاء الجداول اللازمة في قاعدة بيانات Supabase
    """
    supabase = get_supabase_client()

    # ملاحظة: هذه مجرد أمثلة، يجب تعديلها حسب هيكل قاعدة البيانات الفعلي
    # يتم إنشاء الجداول عادةً من خلال واجهة Supabase أو باستخدام SQL

    # مثال على إدخال بيانات في جدول المستخدمين
    # supabase.table('user').insert({
    #     'username': 'example',
    #     'password_hash': 'hashed_password'
    # }).execute()

    return True
