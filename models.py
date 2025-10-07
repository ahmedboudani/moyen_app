from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# ---------------- معلومات عامة عن المؤسسة ----------------
class GeneralInfo(db.Model):
    __tablename__ = "general_info"
    id = db.Column(db.Integer, primary_key=True)
    institution = db.Column(db.String(200), nullable=False)
    directorate = db.Column(db.String(200), nullable=False)
    teacher = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(100), nullable=False)

# ---------------- الأقسام (الفصول) ----------------
class Class(db.Model):
    __tablename__ = "class"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    students = db.relationship("Student", back_populates="class_rel", cascade="all, delete-orphan")


class Student(db.Model):
    __tablename__ = "student"
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    semester = db.Column(db.String(20), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey("class.id"), nullable=False)

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
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False)
    
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
