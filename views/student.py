from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from extensions import db
from models import PlacementDrive, Application
from views.utils import role_required
import os
from werkzeug.utils import secure_filename

student_bp = Blueprint('student', __name__)

@student_bp.route('/dashboard')
@login_required
@role_required('student')
def dashboard():
    applications = Application.query.filter_by(student_id=current_user.student_profile.id).all()
    return render_template('student/dashboard.html', applications=applications)

@student_bp.route('/drives')
@login_required
@role_required('student')
def available_drives():
    drives = PlacementDrive.query.filter_by(status='approved').all()
    applied_drives = [app.drive_id for app in current_user.student_profile.applications]
    return render_template('student/drives.html', drives=drives, applied_drives=applied_drives)

@student_bp.route('/apply/<int:drive_id>', methods=['POST'])
@login_required
@role_required('student')
def apply_drive(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    if drive.status != 'approved': return redirect(url_for('student.available_drives'))
        
    existing_application = Application.query.filter_by(
        student_id=current_user.student_profile.id, drive_id=drive_id).first()
    
    if not existing_application:
        new_app = Application(student_id=current_user.student_profile.id, drive_id=drive_id, status='applied')
        db.session.add(new_app)
        db.session.commit()
    return redirect(url_for('student.dashboard'))

@student_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@role_required('student')
def profile():
    if request.method == 'POST':
        current_user.student_profile.name = request.form.get('name')
        current_user.student_profile.contact = request.form.get('contact')
        
        resume = request.files.get('resume')
        if resume and resume.filename != '':
            filename = f"user_{current_user.id}_{secure_filename(resume.filename)}"
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            resume.save(filepath)
            current_user.student_profile.resume_filename = filename
            
        db.session.commit()
        return redirect(url_for('student.profile'))
        
    return render_template('student/profile.html')