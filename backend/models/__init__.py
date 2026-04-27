from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_blacklisted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.now())

    def get_id(self):
        return str(self.id)


class StudentProfile(db.Model):
    __tablename__ = 'student_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)

    name = db.Column(db.String(100), nullable=False)
    roll_number = db.Column(db.String(50), nullable=False, unique=True)
    branch = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    cgpa = db.Column(db.Float, nullable=False)

    phone = db.Column(db.String(20))
    resume_stored_name = db.Column(db.String(255))

    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    user = db.relationship('User', backref=db.backref('student_profile', uselist=False))


class CompanyProfile(db.Model):
    __tablename__ = 'company_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)

    company_name = db.Column(db.String(200), nullable=False)
    hr_contact = db.Column(db.String(100), nullable=False)
    hr_email = db.Column(db.String(120), nullable=False)

    website = db.Column(db.String(255))

    approval_status = db.Column(db.String(20), default='pending')
    is_deactivated = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    user = db.relationship('User', backref=db.backref('company_profile', uselist=False))


class PlacementDrive(db.Model):
    __tablename__ = 'placement_drives'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company_profiles.id'), nullable=False)

    job_title = db.Column(db.String(200), nullable=False)
    job_description = db.Column(db.Text, nullable=False)

    eligibility_branches = db.Column(db.String(500))
    eligible_years = db.Column(db.String(50))

    min_cgpa = db.Column(db.Float, nullable=False)
    application_deadline = db.Column(db.DateTime, nullable=False)

    status = db.Column(db.String(20), default='pending')

    package_info = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    company = db.relationship('CompanyProfile', backref=db.backref('placement_drives', lazy='dynamic'))
    applications = db.relationship('Application', back_populates='placement_drive', lazy='dynamic', cascade='all, delete-orphan')


class Application(db.Model):
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('placement_drives.id'), nullable=False)

    application_date = db.Column(db.DateTime, default=db.func.now())
    status = db.Column(db.String(30), default='applied')

    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    student = db.relationship('StudentProfile', backref=db.backref('applications', lazy='dynamic'))
    placement_drive = db.relationship('PlacementDrive', back_populates='applications')

    __table_args__ = (db.UniqueConstraint('student_id', 'drive_id', name='unique_student_drive'),)