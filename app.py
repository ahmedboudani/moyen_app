from models import db, Class, Student, Grade, GeneralInfo
from config import Config
from export_pdf import export_to_pdf
import pandas as pd
import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, send_file, jsonify,flash , redirect,url_for
import openpyxl
from openpyxl import load_workbook # ✨ المكتبة الجديدة         # ✨ للتعامل مع الملف في الذا
import io
from openpyxl.utils import coordinate_to_tuple
app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = "tu_clave_secreta_aqui"  # Agrega esta línea
db.init_app(app)
# ✅ توحيد أسماء الفصول
ALL_SEMESTERS = ["الفصل الأول", "الفصل الثاني", "الفصل الثالث"]
ALL_SUBJECTS = [
    "الرياضيات", "اللغة العربية", "اللغة الفرنسية", "اللغة الإنجليزية",
    "العلوم الطبيعية", "العلوم الفيزيائية", "التاريخ", "الجغرافيا",
    "التربية الإسلامية", "التربية المدنية", "التربية البدنية",
    "المعلوماتية", "الفنون التشكيلية", "الموسيقى"
]

@app.context_processor
def inject_general_info():
    info = GeneralInfo.query.first()
    return dict(general_info=info)

with app.app_context():
    db.create_all()

# ---------------- الصفحة الرئيسية ----------------
@app.route("/", methods=["GET", "POST"])
def index():
    info = GeneralInfo.query.first()

    if request.method == "POST":
        institution = request.form.get("institution")
        directorate = request.form.get("directorate")
        teacher = request.form.get("teacher")
        subject = request.form.get("subject")

        if info:
            info.institution = institution
            info.directorate = directorate
            info.teacher = teacher
            info.subject = subject
        else:
            info = GeneralInfo(
                institution=institution,
                directorate=directorate,
                teacher=teacher,
                subject=subject
            )
            db.session.add(info)
        db.session.commit()

    return render_template("index.html", info=info, subjects=ALL_SUBJECTS)


@app.route("/delete_info", methods=["POST"])
def delete_info():
    GeneralInfo.query.delete()
    db.session.commit()
    return redirect(url_for("index"))

# ---------------- إدارة الأقسام ----------------
@app.route("/classes", methods=["GET", "POST"])
def classes():
    if request.method == "POST":
        name = request.form["name"]
        if name:
            db.session.add(Class(name=name))
            db.session.commit()
        return redirect(url_for("classes"))
    return render_template("classes.html", classes=Class.query.all())

@app.route("/class/<int:id>/delete")
def delete_class(id):
    db.session.delete(Class.query.get_or_404(id))
    db.session.commit()
    return redirect(url_for("classes"))

@app.route("/class/<int:id>/edit", methods=["POST"])
def edit_class(id):
    c = Class.query.get_or_404(id)
    c.name = request.form["name"]
    db.session.commit()
    return redirect(url_for("classes"))

# ---------------- إدارة التلاميذ ----------------
@app.route("/students", methods=["GET", "POST"])
def students():
    if request.method == "POST":
        fullname = request.form["fullname"]
        class_id = request.form["class_id"]

        if fullname and class_id:
            try:
                for sem in ALL_SEMESTERS:
                    s = Student(fullname=fullname, class_id=class_id, semester=sem)
                    db.session.add(s)
                db.session.commit()
            except Exception:
                db.session.rollback()
        return redirect(url_for("students", semester=request.args.get('semester', ALL_SEMESTERS[0])))

    current_semester = request.args.get('semester', ALL_SEMESTERS[0])
    students = Student.query.filter(Student.semester == current_semester).order_by(Student.fullname).all()

    return render_template(
        "students.html",
        students=students,
        classes=Class.query.all(),
        semesters=ALL_SEMESTERS,
        current_semester=current_semester
    )

@app.route("/student/<int:id>/delete")
def delete_student(id):
    student = Student.query.get_or_404(id)
    semester = student.semester
    db.session.delete(student)
    db.session.commit()
    return redirect(url_for("students", semester=semester))

@app.route("/student/<int:student_id>/edit", methods=["GET", "POST"])
def edit_student(student_id):
    student = Student.query.get_or_404(student_id)
    if request.method == "POST":
        student.fullname = request.form["fullname"]
        student.class_id = request.form["class_id"]
        student.semester = request.form["semester"]
        db.session.commit()
        return redirect(url_for("students", semester=student.semester))

    return render_template("edit_student.html", student=student, classes=Class.query.all(), semesters=ALL_SEMESTERS)

# ---------------- إدارة العلامات ----------------
@app.route("/grades/<int:student_id>", methods=["GET", "POST"])
def grades(student_id):
    student = Student.query.get_or_404(student_id)
    if request.method == "POST":
        g = Grade(
            assessment=float(request.form["assessment"]),
            test=float(request.form["test"]),
            exam=float(request.form["exam"]),
            student_id=student.id,
            semester=request.form["semester"]
        )
        db.session.add(g)
        db.session.commit()
        return redirect(url_for("grades", student_id=student.id))

    return render_template("grades.html", student=student, grades=student.grades, semesters=ALL_SEMESTERS)

@app.route("/grade/<int:grade_id>/edit", methods=["GET", "POST"])
def edit_grade(grade_id):
    grade = Grade.query.get_or_404(grade_id)
    student = grade.student
    if request.method == "POST":
        grade.assessment = float(request.form["assessment"])
        grade.test = float(request.form["test"])
        grade.exam = float(request.form["exam"])
        db.session.commit()
        return redirect(url_for("grades", student_id=student.id))
    return render_template("edit_grade.html", grade=grade, student=student)

# ---------------- عرض النتائج ----------------
@app.route("/results")
def results():
    class_id = request.args.get("class_id")
    semester = request.args.get("semester")
    query = Student.query

    if class_id and class_id.isdigit():
        query = query.filter(Student.class_id == int(class_id))
    if semester:
        query = query.filter(Student.semester == semester)

    students_with_grades = []
    all_students = query.order_by(Student.fullname).all()
    for student in all_students:
        grades_for_semester = [g for g in student.grades if g.semester == semester]
        student.grades_for_semester = grades_for_semester
        students_with_grades.append(student)

    stats = calculate_statistics(students_with_grades, semester)

    return render_template(
        "results.html",
        students=students_with_grades,
        classes=Class.query.all(),
        selected_class=int(class_id) if class_id and class_id.isdigit() else None,
        selected_semester=semester,
        semesters=ALL_SEMESTERS,
        num_students=stats['num_students'],
        class_average=stats['class_average'],
        success_percentage=stats['success_percentage']
    )
def calculate_statistics(students, semester):
    num_students = len(students)  # كل التلاميذ
    total_student_averages = 0
    successful_students = 0
    counted_students = 0  # فقط الذين لديهم نقاط

    for student in students:
        student_grades_for_semester = student.grades_for_semester
        if not student_grades_for_semester:
            continue  # تجاهل من لا يملك نقاطًا

        student_total = sum(g.average for g in student_grades_for_semester)
        student_average = student_total / len(student_grades_for_semester)

        total_student_averages += student_average
        counted_students += 1

        if student_average >= 10:
            successful_students += 1

    # الحساب فقط من التلاميذ الذين عندهم نقاط
    class_average = total_student_averages / counted_students if counted_students else 0
    success_percentage = (successful_students / counted_students) * 100 if counted_students else 0

    return {
        'num_students': num_students,            # جميع التلاميذ
        'counted_students': counted_students,    # التلاميذ المعبأة نقاطهم
        'class_average': class_average,          # المعدل فقط من المعبأين
        'success_percentage': success_percentage # نسبة النجاح فقط من المعبأين
    }


@app.route("/export/pdf")
def export_pdf_route():
    class_id = request.args.get("class_id")
    semester = request.args.get("semester")

    query = Student.query
    class_name = None
    if class_id and class_id.isdigit():
        query = query.filter(Student.class_id == int(class_id))
        class_obj = Class.query.get(int(class_id))
        if class_obj:
            class_name = class_obj.name

    if semester:
        query = query.filter(Student.semester == semester)

    students_with_grades = []
    all_students = query.all()
    for student in all_students:
        grades_for_semester = [g for g in student.grades if g.semester == semester]
        student.grades_for_semester = grades_for_semester
        students_with_grades.append(student)

    # ✅ استخدام نفس الدالة الموحدة
    stats = calculate_statistics(students_with_grades, semester)

    # بيانات إضافية (المؤسسة، المديرية...)
    general_info = GeneralInfo.query.first()

    pdf_filename = "report.pdf"
    export_to_pdf(
        students_with_grades,
        class_name,
        semester,
        stats['num_students'],
        stats['class_average'],
        stats['success_percentage'],
        info=general_info,
        filename=pdf_filename
    )

    return send_file(pdf_filename, as_attachment=True)
# ---------------- استيراد من Excel ---------------
import tempfile
@app.route("/import_excel", methods=["POST"])
def import_excel():
    file = request.files.get("file")
    if not file:
        flash("لم يتم اختيار ملف", "error")
        return redirect(url_for("students"))

    # الحصول على اسم الصفحة المحددة
    sheet_name = request.form.get("sheet_name")
    
    # الحصول على سطر البداية من النموذج
    start_row = request.form.get("start_row", "3")
    try:
        start_row = int(start_row) - 1  # تحويل إلى فهرس (يبدأ من 0)
        if start_row < 0:
            start_row = 0
    except ValueError:
        start_row = 2  # قيمة افتراضية (السطر 3)
    
    # الحصول على القسم المحدد
    class_id = request.form.get("class_id")
    
    try:
        # التحقق من وجود القسم المحدد
        selected_class = None
        if class_id and class_id.isdigit():
            selected_class = Class.query.get(int(class_id))
        
        # إذا لم يتم تحديد قسم أو القسم غير موجود، استخدم القسم الافتراضي
        if not selected_class:
            selected_class = Class.query.first()
            if not selected_class:
                selected_class = Class(name="القسم الافتراضي")
                db.session.add(selected_class)
                db.session.commit()
      
        sheet_index = 0  # قيمة افتراضية
        if sheet_name == "Sheet1" or sheet_name == "ورقة1":
            sheet_index = 0
        elif sheet_name == "Sheet2" or sheet_name == "ورقة2":
            sheet_index = 1
        elif sheet_name == "Sheet3" or sheet_name == "ورقة3":
            sheet_index = 2

        # استخدام الفهرس بدلاً من الاسم
        df = pd.read_excel(file, header=None, sheet_name=sheet_index)

        # التحقق من أن الملف يحتوي على عدد كافٍ من الصفوف والأعمدة
        if df.shape[0] < start_row + 1 or df.shape[1] < 3:
            flash(f"بنية الملف غير صحيحة. يجب أن يحتوي الملف على بيانات بدءًا من السطر {start_row + 1} وعلى الأقل 3 أعمدة.", "error")
            return redirect(url_for("students"))

        # عدد الطلاب الذين تمت إضافتهم
        students_added = 0

        # بدء القراءة من السطر المحدد
        for index, row in df.iloc[start_row:].iterrows():
            try:
                # قراءة البيانات من العمود E (الفهرس 4) فما فوق
                # تجاهل الأعمدة قبل E
                lastname = str(row.get(4, "")).strip()  # العمود E
                firstname = str(row.get(5, "")).strip()  # العمود F
                
                # تخطي الصفوف الفارغة
                if not lastname or not firstname:
                    continue
                    
                # دمج الاسم واللقب لتكوين الاسم الكامل
                fullname = f"{lastname} {firstname}"
                
                # إضافة الطالب لكل فصل دراسي
                for sem in ALL_SEMESTERS:
                    # التحقق من عدم وجود الطالب مسبقًا في نفس الفصل
                    exists = Student.query.filter_by(
                        fullname=fullname,
                        class_id=selected_class.id,
                        semester=sem
                    ).first()
                    
                    if not exists:
                        student = Student(
                            fullname=fullname,
                            class_id=selected_class.id,
                            semester=sem
                        )
                        db.session.add(student)
                        students_added += 1
            
            except Exception as row_error:
                # تجاهل الأخطاء في صف واحد والاستمرار في الصفوف الأخرى
                continue
        
        # حفظ التغييرات في قاعدة البيانات
        db.session.commit()
        
        # إضافة رسالة نجاح
        if students_added > 0:
            flash(f"تم استيراد {students_added} طالب بنجاح من الصفحة {sheet_name} إلى القسم {selected_class.name}", "success")
        else:
            flash("لم يتم إضافة أي طالب جديد", "info")
        
        # إعادة توجيه المستخدم إلى صفحة الطلاب
        return redirect(url_for("students"))
            
    except Exception as e:
        # التراجع عن التغييرات في حالة حدوث خطأ
        db.session.rollback()
        
        # إضافة رسالة خطأ
        flash(f"حدث خطأ أثناء استيراد الملف: {str(e)}", "error")
        
        # إعادة توجيه المستخدم إلى صفحة الطلاب
        return redirect(url_for("students"))

def get_top_left_cell(sheet, cell_ref):
    """
    ترجع إحداثيات أول خلية في مجموعة الدمج إذا كانت الخلية مدموجة،
    أو نفس الخلية إذا لم تكن مدموجة.
    """
    for merged_range in sheet.merged_cells.ranges:
        if cell_ref in merged_range:
            return merged_range.min_row, merged_range.min_col
    return coordinate_to_tuple(cell_ref)

def get_top_left_cell(sheet, cell_ref):
    for merged_range in sheet.merged_cells.ranges:
        if cell_ref in merged_range:
            return merged_range.min_row, merged_range.min_col
    return coordinate_to_tuple(cell_ref)
import sqlite3
import json
@app.route("/export_excel", methods=["POST"])
def export_excel():
    try:
        # استلام الملف والبيانات
        if 'excel_file' not in request.files:
            return jsonify({"success": False, "error": "لم يتم تحديد ملف"})
        
        excel_file = request.files['excel_file']
        if excel_file.filename == '':
            return jsonify({"success": False, "error": "لم يتم اختيار ملف"})
            
        sheet_name = request.form.get('sheet_name')
        students_data_json = request.form.get('students_data')
        
        if not sheet_name or not students_data_json:
            return jsonify({"success": False, "error": "بيانات غير مكتملة"})
        
        # تحويل البيانات من JSON إلى قائمة
        students_data = json.loads(students_data_json)
        
        # قراءة الملف في الذاكرة
        file_data = excel_file.read()
        input_buffer = io.BytesIO(file_data)
        
        # فتح الملف باستخدام openpyxl
        try:
            workbook = load_workbook(input_buffer)
            
            # تحديد الصفحة المطلوبة (تحويل من رقم إلى فهرس)
            sheet_index = int(sheet_name) - 1
            if sheet_index < 0 or sheet_index >= len(workbook.sheetnames):
                return jsonify({"success": False, "error": f"الصفحة رقم {sheet_name} غير موجودة"})
            
            sheet = workbook.worksheets[sheet_index]
            
            # كتابة البيانات ابتداءً من السطر 9
            start_row = 9
            
            for i, student in enumerate(students_data):
                row = start_row + i
                
                # كتابة البيانات في الأعمدة المحددة
                sheet[f'E{row}'] = student.get('assessment', '')  # التقويم في العمود E
                sheet[f'F{row}'] = student.get('test', '')        # الفرض في العمود F
                sheet[f'G{row}'] = student.get('exam', '')        # الاختبار في العمود G
                sheet[f'H{row}'] = student.get('note', '')        # الملاحظات في العمود H
            
            # حفظ الملف في الذاكرة
            output_buffer = io.BytesIO()
            workbook.save(output_buffer)
            output_buffer.seek(0)
            
            # إرسال الملف للتنزيل
            return send_file(
                output_buffer,
                as_attachment=True,
                download_name=excel_file.filename,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            
        except Exception as e:
            print(f"Error processing Excel file: {str(e)}")
            return jsonify({"success": False, "error": str(e)})
            
    except Exception as e:
        print(f"General error: {str(e)}")
        return jsonify({"success": False, "error": str(e)})


if __name__ == "__main__":
    app.run(debug=True)