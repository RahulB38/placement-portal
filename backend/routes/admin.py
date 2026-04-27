from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
from models import db, User, StudentProfile, CompanyProfile, PlacementDrive, Application
from extensions import cache

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return wrapper


def apply_search_filters(query, search, fields, id_fields=None):
    if not search:
        return query
    value = search.strip()
    numeric = int(value) if value.isdigit() else None
    conditions = [f.ilike(f'%{value}%') for f in fields]
    if numeric and id_fields:
        conditions += [f == numeric for f in id_fields]
    return query.filter(db.or_(*conditions))


def fmt_date(d):
    return d.isoformat() if d else None


@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    key = 'admin_dashboard_stats_v2'
    data = cache.get(key)
    if data is None:
        recent_list = [
            {
                'student_name': a.student.name if a.student else 'N/A',
                'roll_number': a.student.roll_number if a.student else '',
                'drive_title': a.placement_drive.job_title if a.placement_drive else '',
                'company_name': a.placement_drive.company.company_name if a.placement_drive and a.placement_drive.company else '',
                'status': a.status,
                'application_date': fmt_date(a.application_date)
            }
            for a in Application.query.order_by(Application.application_date.desc()).limit(6)
        ]

        data = {
            'total_students': StudentProfile.query.join(User).filter(User.is_blacklisted == False).count(),
            'registered_students': StudentProfile.query.count(),
            'placed_students': db.session.query(Application.student_id).filter_by(status='selected').distinct().count(),
            'blacklisted_students': StudentProfile.query.join(User).filter(User.is_blacklisted == True).count(),
            'total_companies': CompanyProfile.query.filter_by(approval_status='approved', is_deactivated=False).count(),
            'total_drives': PlacementDrive.query.filter_by(status='approved').count(),
            'total_applications': Application.query.count(),
            'pending_companies': CompanyProfile.query.filter_by(approval_status='pending').count(),
            'pending_drives': PlacementDrive.query.filter_by(status='pending').count(),
            'recent_applications': recent_list
        }
        cache.set(key, data, timeout=60)
    return jsonify(data)


@admin_bp.route('/companies')
@login_required
@admin_required
def list_companies():
    search = request.args.get('search', '')
    query = apply_search_filters(
        CompanyProfile.query.join(User), search,
        [CompanyProfile.company_name, CompanyProfile.hr_contact, CompanyProfile.hr_email, User.email],
        [CompanyProfile.id, CompanyProfile.user_id]
    )

    return jsonify([
        {
            'id': c.id,
            'company_name': c.company_name,
            'hr_contact': c.hr_contact,
            'hr_email': c.hr_email,
            'website': c.website,
            'status': 'blacklisted' if c.is_deactivated else c.approval_status,
            'user_id': c.user_id
        }
        for c in query.all()
    ])


@admin_bp.route('/companies/<int:id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_company(id):
    company = CompanyProfile.query.get_or_404(id)
    action = request.get_json().get('action', 'approve')
    company.approval_status = 'approved' if action == 'approve' else 'rejected'
    db.session.commit()
    cache.clear()
    return jsonify({'message': f'Company {action}d successfully'})


@admin_bp.route('/companies/<int:id>/deactivate', methods=['POST'])
@login_required
@admin_required
def toggle_company(id):
    company = CompanyProfile.query.get_or_404(id)
    company.is_deactivated = not company.is_deactivated
    db.session.commit()
    cache.clear()
    return jsonify({'message': 'Company blacklisted' if company.is_deactivated else 'Company reactivated'})


@admin_bp.route('/students')
@login_required
@admin_required
def list_students():
    search = request.args.get('search', '')
    query = apply_search_filters(
        StudentProfile.query.join(User), search,
        [StudentProfile.name, StudentProfile.roll_number, StudentProfile.phone, User.email],
        [StudentProfile.id, StudentProfile.user_id]
    )

    return jsonify([
        {
            'id': s.id,
            'name': s.name,
            'roll_number': s.roll_number,
            'branch': s.branch,
            'year': s.year,
            'cgpa': s.cgpa,
            'email': s.user.email if s.user else '',
            'user_id': s.user_id,
            'is_blacklisted': s.user.is_blacklisted if s.user else False
        }
        for s in query.all()
    ])


@admin_bp.route('/students/<int:user_id>/blacklist', methods=['POST'])
@login_required
@admin_required
def blacklist_student(user_id):
    user = User.query.get_or_404(user_id)
    if user.role != 'student':
        return jsonify({'error': 'Invalid user'}), 400
    print(user.id)
    stu=StudentProfile.query.filter_by(user_id=user.id)

    user.is_blacklisted = not user.is_blacklisted
    db.session.commit()
    cache.clear()
    return jsonify({'message': 'Student blacklisted' if user.is_blacklisted else 'Student reactivated'})


@admin_bp.route('/drives')
@login_required
@admin_required
def list_drives():
    return jsonify([
        {
            'id': d.id,
            'job_title': d.job_title,
            'company_name': d.company.company_name if d.company else 'N/A',
            'status': d.status,
            'application_deadline': fmt_date(d.application_deadline),
            'applicants_count': d.applications.count()
        }
        for d in PlacementDrive.query.all()
    ])


@admin_bp.route('/drives/<int:id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_drive(id):
    drive = PlacementDrive.query.get_or_404(id)
    action = request.get_json().get('action', 'approve')
    drive.status = 'approved' if action == 'approve' else 'rejected'
    db.session.commit()
    cache.clear()
    return jsonify({'message': f'Drive {action}d successfully'})


@admin_bp.route('/applications')
@login_required
@admin_required
def list_applications():
    return jsonify([
        {
            'id': a.id,
            'student_name': a.student.name if a.student else 'N/A',
            'roll_number': a.student.roll_number if a.student else 'N/A',
            'drive_title': a.placement_drive.job_title if a.placement_drive else 'N/A',
            'company_name': a.placement_drive.company.company_name if a.placement_drive and a.placement_drive.company else 'N/A',
            'status': a.status,
            'application_date': fmt_date(a.application_date)
        }
        for a in Application.query.all()
    ])


@admin_bp.route('/statistics')
@login_required
@admin_required
def statistics():
    return jsonify({
        'total_drives': PlacementDrive.query.filter_by(status='approved').count(),
        'total_applications': Application.query.count(),
        'selected_count': Application.query.filter_by(status='selected').count(),
        'shortlisted_count': Application.query.filter_by(status='shortlisted').count(),
        'students_placed': db.session.query(Application.student_id).filter_by(status='selected').distinct().count()
    })