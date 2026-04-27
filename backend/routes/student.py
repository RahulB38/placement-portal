import os
import uuid
from flask import Blueprint, request, jsonify, current_app, send_file
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime
from werkzeug.utils import secure_filename
from models import db, StudentProfile, PlacementDrive, Application
from extensions import cache
from form_chk import parse_year_val, parse_cgpa_val, phone_ok
from routes.auth import DEACT_MSG

student_bp = Blueprint('student', __name__)


def student_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'student':
            return jsonify({'error': 'Student access required'}), 403
        if current_user.is_blacklisted or not current_user.is_active:
            return jsonify({'error': DEACT_MSG}), 403
        return f(*args, **kwargs)
    return wrapper


def get_student():
    return StudentProfile.query.filter_by(user_id=current_user.id).first()


def _resume_path(stored_name):
    if not stored_name:
        return None
    folder = current_app.config['UPLOAD_FOLDER']
    return os.path.join(folder, stored_name)


def _is_pdf_file(storage):
    if not storage or not storage.filename:
        return False
    name = secure_filename(storage.filename)
    if not name.lower().endswith('.pdf'):
        return False
    storage.stream.seek(0)
    head = storage.stream.read(4)
    storage.stream.seek(0)
    return head == b'%PDF'


def fmt_date(d):
    return d.isoformat() if d else None


def is_eligible(student, drive):
    if student.cgpa < drive.min_cgpa:
        return False, 'CGPA below minimum required'

    if drive.eligibility_branches:
        branches = [b.strip().lower() for b in drive.eligibility_branches.split(',') if b.strip()]
        if (student.branch or '').strip().lower() not in branches:
            return False, 'Your branch is not eligible for this drive'

    if drive.eligible_years:
        years = [y.strip() for y in drive.eligible_years.split(',') if y.strip()]
        if str(student.year) not in years:
            return False, 'Your year is not eligible for this drive'

    return True, None


def _drive_dict(d, applied_ids, student):
    co = d.company
    co_blk = bool(co and co.is_deactivated)
    eligible, reason = is_eligible(student, d)
    return {
        'id': d.id,
        'job_title': d.job_title,
        'company_name': co.company_name if co else 'N/A',
        'min_cgpa': d.min_cgpa,
        'deadline': fmt_date(d.application_deadline),
        'job_description': d.job_description or '',
        'eligibility_branches': d.eligibility_branches or '',
        'eligible_years': d.eligible_years or '',
        'package_info': d.package_info or '',
        'applied': d.id in applied_ids,
        'eligible': eligible and not co_blk,
        'eligibility_reason': 'Company is blacklisted by placement cell' if co_blk else reason,
        'company_blacklisted': co_blk
    }


def _app_dict(a):
    pd = a.placement_drive
    co = pd.company if pd else None
    return {
        'id': a.id,
        'drive_id': pd.id if pd else None,
        'job_title': pd.job_title if pd else '',
        'company_name': co.company_name if co else '',
        'status': a.status,
        'application_date': fmt_date(a.application_date),
        'company_blacklisted': bool(co and co.is_deactivated)
    }


@student_bp.route('/dashboard')
@login_required
@student_required
def dashboard():
    student = get_student()
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404

    applications = Application.query.filter_by(student_id=student.id).all()
    applied_ids = {a.drive_id for a in applications}

    key = f'student_drives_{student.id}'
    ids = cache.get(key)
    if ids is None:
        ids = [
            d.id for d in PlacementDrive.query.filter_by(status='approved')
            .filter(PlacementDrive.application_deadline >= datetime.utcnow())
        ]
        cache.set(key, ids, timeout=120)

    drives = PlacementDrive.query.filter(PlacementDrive.id.in_(ids)).all() if ids else []

    return jsonify({
        'student': {
            'id': student.id,
            'name': student.name,
            'roll_number': student.roll_number,
            'branch': student.branch,
            'cgpa': student.cgpa,
            'year': student.year
        },
        'drives': [_drive_dict(d, applied_ids, student) for d in drives],
        'applications': [_app_dict(a) for a in applications]
    })


@student_bp.route('/profile', methods=['GET', 'PUT'])
@login_required
@student_required
def profile():
    student = get_student()
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404

    if request.method == 'GET':
        return jsonify({
            'id': student.id,
            'name': student.name,
            'roll_number': student.roll_number,
            'branch': student.branch,
            'year': student.year,
            'cgpa': student.cgpa,
            'phone': student.phone,
            'has_resume': bool(student.resume_stored_name)
        })

    data = request.get_json() or {}

    y, err = parse_year_val(data.get('year', student.year))
    if err:
        return jsonify({'error': err}), 400

    c, err = parse_cgpa_val(data.get('cgpa', student.cgpa))
    if err:
        return jsonify({'error': err}), 400

    phone = data.get('phone', student.phone)
    ok_p, err_p = phone_ok(phone)
    if not ok_p:
        return jsonify({'error': err_p}), 400

    student.name = data.get('name', student.name)
    student.branch = data.get('branch', student.branch)
    student.year = y
    student.cgpa = c
    student.phone = phone.strip() if phone else None

    db.session.commit()
    cache.delete(f'student_drives_{student.id}')

    return jsonify({'message': 'Profile updated successfully'})


@student_bp.route('/resume', methods=['POST'])
@login_required
@student_required
def upload_resume():
    student = get_student()
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404

    f = request.files.get('file')
    if not f or not f.filename:
        return jsonify({'error': 'No file uploaded'}), 400

    if not _is_pdf_file(f):
        return jsonify({'error': 'Only PDF files are allowed'}), 400

    stored = f'{student.id}_{uuid.uuid4().hex}.pdf'
    dest = os.path.join(current_app.config['UPLOAD_FOLDER'], stored)

    old = student.resume_stored_name
    f.save(dest)

    student.resume_stored_name = stored
    db.session.commit()

    if old and old != stored:
        old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], old)
        if os.path.isfile(old_path):
            try:
                os.remove(old_path)
            except OSError:
                pass

    return jsonify({'message': 'Resume uploaded successfully', 'has_resume': True})


@student_bp.route('/resume', methods=['GET'])
@login_required
@student_required
def download_own_resume():
    student = get_student()
    if not student or not student.resume_stored_name:
        return jsonify({'error': 'No resume on file'}), 404

    path = _resume_path(student.resume_stored_name)
    if not path or not os.path.isfile(path):
        return jsonify({'error': 'Resume file missing'}), 404

    return send_file(
        path,
        mimetype='application/pdf',
        as_attachment=False,
        download_name=f'resume_{student.roll_number}.pdf'
    )


@student_bp.route('/apply/<int:drive_id>', methods=['POST'])
@login_required
@student_required
def apply(drive_id):
    student = get_student()
    drive = PlacementDrive.query.get_or_404(drive_id)

    if drive.status != 'approved':
        return jsonify({'error': 'This drive is not open for applications'}), 400

    if drive.company and drive.company.is_deactivated:
        return jsonify({'error': 'This company is currently blacklisted'}), 400

    if drive.application_deadline < datetime.utcnow():
        return jsonify({'error': 'Application deadline has passed'}), 400

    if Application.query.filter_by(student_id=student.id, drive_id=drive_id).first():
        return jsonify({'error': 'You have already applied to this drive'}), 400

    ok, reason = is_eligible(student, drive)
    if not ok:
        return jsonify({'error': f'Not eligible: {reason}'}), 400

    db.session.add(Application(student_id=student.id, drive_id=drive_id))
    db.session.commit()
    cache.delete(f'student_drives_{student.id}')

    return jsonify({'message': 'Application submitted successfully'}), 201


@student_bp.route('/export-csv', methods=['POST'])
@login_required
@student_required
def export_csv():
    from tasks.export_tasks import export_applications_csv
    student = get_student()
    task = export_applications_csv.delay(student.id)
    return jsonify({'message': 'Export started', 'task_id': task.id})


@student_bp.route('/export-status/<task_id>')
@login_required
@student_required
def export_status(task_id):
    from celery_app import celery_app
    res = celery_app.AsyncResult(task_id)

    if res.ready():
        return jsonify({'status': 'complete', 'result': res.result}) if res.successful() \
            else jsonify({'status': 'failed', 'error': str(res.result)})

    return jsonify({'status': 'pending'})