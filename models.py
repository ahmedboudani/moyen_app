from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    general_info = db.relationship("GeneralInfo", back_populates="user", cascade="all, delete-orphan")
    classes = db.relationship("Class", back_populates="user", cascade="all, delete-orphan")
    students = db.relationship("Student", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# ---------------- معلومات عامة عن المؤسسة ----------------
class GeneralInfo(db.Model):
    __tablename__ = "general_info"
    id = db.Column(db.Integer, primary_key=True)
    institution = db.Column(db.String(200), nullable=False)
    directorate = db.Column(db.String(200), nullable=False)
    teacher = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User", back_populates="general_info")

# ---------------- الأقسام (الفصول) ----------------
class Class(db.Model):
    __tablename__ = "class"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User", back_populates="classes")
    students = db.relationship("Student", back_populates="class_rel", cascade="all, delete-orphan")

class Student(db.Model):
    __tablename__ = "student"
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    semester = db.Column(db.String(20), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey("class.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User", back_populates="students")

    # علاقات
    class_rel = db.relationship("Class", back_populates="students")
    grades = db.relationship(
        "Grade",
        back_populates="student",
        cascade="all, delete-orphan"
    )


class Grade(db.Model):
    __tablename__ = "grade"
    id = db.Column(db.Integer, primary_key=True)
    assessment = db.Column(db.Float, nullable=False, default=0.0)  # التقويم
    test = db.Column(db.Float, nullable=False, default=0.0)        # الفرض
    exam = db.Column(db.Float, nullable=False, default=0.0)        # الاختبار
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    
    # *** التعديل 2: إضافة عمود الفصل الدراسي لجدول العلامات (ضروري) ***
    semester = db.Column(db.String(50), nullable=False) 

    # العلاقة مع الطالب
    student = db.relationship("Student", back_populates="grades")

    @property
    def avg_controle(self):
        return round((self.assessment + self.test) / 2, 2)

    @property
    def average(self):
        return round((self.avg_controle + self.exam * 2) / 3, 2)

    @property
    def note(self):
        avg = self.average
        if avg >= 17:
            return "نتائج ممتازة"
        elif avg > 13.5:
            return "نتائج جيدة"
        elif avg > 10:
            return "نتائج مقبولة"
        elif avg > 7.5:
            return "نتائج غير كافية"
        else:
            return "نتائج غير مرضية"