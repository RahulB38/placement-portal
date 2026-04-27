import os
from flask import Blueprint, request, jsonify, current_app, send_file
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime
from models import db, CompanyProfile, PlacementDrive, Application
from routes.auth import DEACT_MSG
from form_chk import parse_min_cgpa_val

company_bp = Blueprint('company', __name__)


def company_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'company':
            return jsonify({'error': 'Company access required'}), 403
        prof = CompanyProfile.query.filter_by(user_id=current_user.id).first()
        if prof and prof.is_deactivated:
            return jsonify({'error': DEACT_MSG}), 403
        return f(*args, **kwargs)
    return wrapper


def get_company():
    return CompanyProfile.query.filter_by(user_id=current_user.id).first()


def parse_datetime(value):
    try:
        dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
        return dt.replace(tzinfo=None) if dt.tzinfo else dt
    except Exception:
        return None


def fmt_date(d):
    return d.isoformat() if d else None


def owned_drive(drive_id):
    company = get_company()
    drive = PlacementDrive.query.get_or_404(drive_id)
    return (company, drive) if drive.company_id == company.id else (company, None)


@company_bp.route('/dashboard')
@login_required
@company_required
def dashboard():
    company = get_company()
    if not company:
        return jsonify({'error': 'Company profile not found'}), 404

    drives_data = [
        {
            'id': d.id,
            'job_title': d.job_title,
            'status': d.status,
            'applicants_count': d.applications.count(),
            'deadline': fmt_date(d.application_deadline)
        }
        for d in PlacementDrive.query.filter_by(company_id=company.id)
    ]

    return jsonify({
        'company': {
            'id': company.id,
            'company_name': company.company_name,
            'hr_contact': company.hr_contact,
            'website': company.website,
            'approval_status': company.approval_status
        },
        'drives': drives_data,
        'total_applicants': sum(d['applicants_count'] for d in drives_data)
    })


@company_bp.route('/drives', methods=['POST'])
@login_required
@company_required
def drives():
    company = get_company()
    if not company:
        return jsonify({'error': 'Company profile not found'}), 404

    data = request.get_json() or {}

    for field in ['job_title', 'job_description', 'min_cgpa', 'application_deadline']:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    mc, err = parse_min_cgpa_val(data.get('min_cgpa'))
    if err:
        return jsonify({'error': err}), 400

    deadline = parse_datetime(data['application_deadline'])
    if not deadline:
        return jsonify({'error': 'Invalid deadline format'}), 400

    branches = data.get('eligibility_branches', '')
    years = data.get('eligible_years', '')

    db.session.add(PlacementDrive(
        company_id=company.id,
        job_title=data['job_title'],
        job_description=data['job_description'],
        eligibility_branches=','.join(branches) if isinstance(branches, list) else branches,
        min_cgpa=mc,
        eligible_years=','.join(map(str, years)) if isinstance(years, list) else str(years),
        application_deadline=deadline,
        package_info=data.get('package_info'),
        status='pending'
    ))
    db.session.commit()

    return jsonify({'message': 'Drive submitted successfully. Pending admin approval.'}), 201


@company_bp.route('/drives/<int:drive_id>/applications')
@login_required
@company_required
def drive_applications(drive_id):
    company, drive = owned_drive(drive_id)
    if not drive:
        return jsonify({'error': 'Unauthorized'}), 403

    return jsonify([
        {
            'id': a.id,
            'student_name': a.student.name if a.student else 'N/A',
            'roll_number': a.student.roll_number if a.student else 'N/A',
            'branch': a.student.branch if a.student else 'N/A',
            'cgpa': a.student.cgpa if a.student else 0,
            'status': a.status,
            'application_date': fmt_date(a.application_date),
            'student_blacklisted': bool(
                a.student and a.student.user and
                (a.student.user.is_blacklisted or not a.student.user.is_active)
            ),
            'has_resume': bool(a.student and a.student.resume_stored_name)
        }
        for a in drive.applications
    ])


@company_bp.route('/applications/<int:app_id>/status', methods=['PUT'])
@login_required
@company_required
def update_application_status(app_id):
    application = Application.query.get_or_404(app_id)
    company = get_company()

    if not application.placement_drive or application.placement_drive.company_id != company.id:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json() or {}
    status = data.get('status')

    if status not in ['applied', 'shortlisted', 'selected', 'rejected']:
        return jsonify({'error': 'Invalid status. Must be one of: applied, shortlisted, selected, rejected'}), 400

    application.status = status
    db.session.commit()
    return jsonify({'message': 'Application status updated successfully'})


@company_bp.route('/applications/<int:app_id>/resume')
@login_required
@company_required
def download_application_resume(app_id):
    application = Application.query.get_or_404(app_id)
    company = get_company()

    if not application.placement_drive or application.placement_drive.company_id != company.id:
        return jsonify({'error': 'Unauthorized'}), 403

    student = application.student
    if not student or not student.resume_stored_name:
        return jsonify({'error': 'No resume on file for this student'}), 404

    path = os.path.join(current_app.config['UPLOAD_FOLDER'], student.resume_stored_name)
    if not os.path.isfile(path):
        return jsonify({'error': 'Resume file missing'}), 404

    return send_file(
        path,
        mimetype='application/pdf',
        as_attachment=False,
        download_name=f'resume_{student.roll_number}.pdf'
    )