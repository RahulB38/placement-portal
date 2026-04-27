from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, StudentProfile, CompanyProfile
from form_chk import parse_year_val, parse_cgpa_val, phone_ok

auth_bp = Blueprint('auth', __name__)

DEACT_MSG = 'User deactivated - contact your placement cell'


def validate_fields(data, fields):
    if not data:
        return 'No data provided'
    for f in fields:
        if not data.get(f):
            return f'{f} is required'
    return None


def create_user(email, password, role):
    user = User(
        email=email,
        password_hash=generate_password_hash(password),
        role=role
    )
    db.session.add(user)
    db.session.flush()
    return user


@auth_bp.route('/register/student', methods=['POST'])
def register_student():
    data = request.get_json()

    error = validate_fields(data, ['email', 'password', 'name', 'roll_number', 'branch', 'year', 'cgpa'])
    if error:
        return jsonify({'error': error}), 400

    y, err = parse_year_val(data.get('year'))
    if err:
        return jsonify({'error': err}), 400

    c, err = parse_cgpa_val(data.get('cgpa'))
    if err:
        return jsonify({'error': err}), 400

    phone = data.get('phone')
    ok_p, err_p = phone_ok(phone)
    if not ok_p:
        return jsonify({'error': err_p}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400

    if StudentProfile.query.filter_by(roll_number=data['roll_number']).first():
        return jsonify({'error': 'Roll number already registered'}), 400

    user = create_user(data['email'], data['password'], 'student')
    profile = StudentProfile(
        user_id=user.id,
        name=data['name'],
        roll_number=data['roll_number'],
        branch=data['branch'],
        year=y,
        cgpa=c,
        phone=phone.strip() if phone else None
    )
    db.session.add(profile)
    db.session.commit()

    return jsonify({'message': 'Registration successful', 'user_id': user.id}), 201


@auth_bp.route('/register/company', methods=['POST'])
def register_company():
    data = request.get_json()

    error = validate_fields(data, ['email', 'password', 'company_name', 'hr_contact', 'hr_email'])
    if error:
        return jsonify({'error': error}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400

    user = create_user(data['email'], data['password'], 'company')
    profile = CompanyProfile(
        user_id=user.id,
        company_name=data['company_name'],
        hr_contact=data['hr_contact'],
        hr_email=data['hr_email'],
        website=data.get('website'),
        approval_status='pending'
    )
    db.session.add(profile)
    db.session.commit()

    return jsonify({'message': 'Your company registration is under review. Please wait for admin approval.', 'user_id': user.id}), 201


def check_company_access(user):
    profile = CompanyProfile.query.filter_by(user_id=user.id).first()
    if not profile:
        return 'Company profile not found'
    if profile.is_deactivated:
        return DEACT_MSG
    if profile.approval_status != 'approved':
        return 'Company registration pending admin approval'
    return None


def attach_profile_data(user, response):
    if user.role == 'student':
        profile = StudentProfile.query.filter_by(user_id=user.id).first()
        if profile:
            response['profile_id'] = profile.id
            response['welcome_name'] = profile.name

    if user.role == 'company':
        profile = CompanyProfile.query.filter_by(user_id=user.id).first()
        if profile:
            response['profile_id'] = profile.id
            response['company_name'] = profile.company_name
            response['welcome_name'] = profile.company_name

    if user.role == 'admin':
        response['welcome_name'] = user.email.split('@')[0] if user.email else 'Admin'

    return response


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400

    user = User.query.filter_by(email=data['email']).first()

    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({'error': 'Incorrect email or password. Please try again.'}), 401

    if user.is_blacklisted or not user.is_active:
        return jsonify({'error': DEACT_MSG}), 403

    if user.role == 'company':
        error = check_company_access(user)
        if error:
            return jsonify({'error': error}), 403

    login_user(user, remember=data.get('remember', False))

    response = {
        'id': user.id,
        'email': user.email,
        'role': user.role,
        'message': 'Login successful'
    }

    response = attach_profile_data(user, response)
    return jsonify(response)


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'})


@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    out = {
        'id': current_user.id,
        'email': current_user.email,
        'role': current_user.role
    }
    return jsonify(attach_profile_data(current_user, out))