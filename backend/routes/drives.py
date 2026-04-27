from flask import Blueprint, request, jsonify
from models import PlacementDrive, CompanyProfile
from extensions import cache

drives_bp = Blueprint('drives', __name__)


def fmt_date(d):
    return d.isoformat() if d else None


def build_drive_response(d):
    co = d.company
    return {
        'id': d.id,
        'job_title': d.job_title,
        'company_name': co.company_name if co else 'N/A',
        'min_cgpa': d.min_cgpa,
        'eligibility_branches': d.eligibility_branches,
        'application_deadline': fmt_date(d.application_deadline),
        'applicants_count': d.applications.count(),
        'company_blacklisted': bool(co and co.is_deactivated)
    }


@drives_bp.route('')
def list_drives():
    search = request.args.get('search', '').strip()
    key = f'drives_{search}'
    data = cache.get(key)

    if data is None:
        query = PlacementDrive.query.filter_by(status='approved')

        if search:
            query = query.join(CompanyProfile).filter(
                PlacementDrive.job_title.ilike(f'%{search}%') |
                CompanyProfile.company_name.ilike(f'%{search}%')
            )

        data = [build_drive_response(d) for d in query]
        cache.set(key, data, timeout=60)

    return jsonify(data)


@drives_bp.route('/<int:id>')
def get_drive(id):
    drive = PlacementDrive.query.get_or_404(id)
    co = drive.company

    return jsonify({
        'id': drive.id,
        'job_title': drive.job_title,
        'job_description': drive.job_description,
        'company_name': co.company_name if co else 'N/A',
        'min_cgpa': drive.min_cgpa,
        'eligibility_branches': drive.eligibility_branches,
        'eligible_years': drive.eligible_years,
        'application_deadline': fmt_date(drive.application_deadline),
        'package_info': drive.package_info,
        'status': drive.status,
        'company_blacklisted': bool(co and co.is_deactivated)
    })