from flask import Flask, render_template, request, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename
from models import db, VisaApplication

basedir = os.path.abspath(os.path.dirname(__file__))

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'instance', 'applications.db')}"
app.config['UPLOAD_FOLDER'] = os.path.join(basedir, UPLOAD_FOLDER)
app.secret_key = 'nexosecret'

# UI 增强：自定义模板目录位置（可选）
app.template_folder = os.path.join(basedir, 'templates')

#初始化DB
db.init_app(app)

with app.app_context():
    db.create_all()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#上传页面
@app.route('/')
def upload_page():
    return render_template('upload.html')

#提交申请
@app.route('/submit_application', methods=['POST'])
def submit_application():
    full_name = request.form['full_name']
    passport_number = request.form['passport_number']
    email = request.form['email']
    phone = request.form['phone']

    photo = request.files.get('photo')
    document = request.files.get('document')

    if not (photo and allowed_file(photo.filename)):
        flash('Invalid or missing photo')
        return redirect(url_for('upload_page'))

    photo_filename = secure_filename(photo.filename)
    photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))

    document_filename = None
    if document and allowed_file(document.filename):
        document_filename = secure_filename(document.filename)
        document.save(os.path.join(app.config['UPLOAD_FOLDER'], document_filename))

    #删除旧申请（若存在）
    existing = VisaApplication.query.filter_by(passport_number=passport_number).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()

    application = VisaApplication(
        full_name=full_name,
        passport_number=passport_number,
        email=email,
        phone=phone,
        photo_filename=photo_filename,
        document_filename=document_filename
    )
    db.session.add(application)
    db.session.commit()

    flash('Application submitted successfully!')
    return redirect(url_for('upload_page'))

#检查护照进度
@app.route('/check_status', methods=['GET', 'POST'])
def check_status():
    result = None
    if request.method == 'POST':
        passport_number = request.form['passport_number']
        application = VisaApplication.query.filter_by(passport_number=passport_number).first()
        result = application
    return render_template('check_status.html', result=result)

#失败后重新上传
@app.route('/reupload/<string:passport_number>', methods=['GET'])
def reupload(passport_number):
    application = VisaApplication.query.filter_by(passport_number=passport_number).first()
    if not application:
        flash("No application found for reupload")
        return redirect(url_for('upload_page'))
    flash("Please re-submit your application")
    return redirect(url_for('upload_page'))

#展示申请列别
@app.route('/admin/applications')
def admin_applications():
    applications = VisaApplication.query.order_by(VisaApplication.submitted_at.desc()).all()
    return render_template('admin_applications.html', applications=applications)

#提交更新状态
@app.route('/admin/update_status/<int:app_id>', methods=['POST'])
def update_status(app_id):
    application = VisaApplication.query.get_or_404(app_id)
    new_status = request.form['status']
    reason = request.form.get('rejection_reason')

    application.status = new_status
    application.rejection_reason = reason if new_status == 'rejected' else None

    db.session.commit()
    flash(f'Status updated to {new_status}')
    return redirect(url_for('admin_applications'))