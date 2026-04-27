import os
import redis
from flask import Flask
from flask_cors import CORS
from config import Config
from extensions import login_manager, cache, mail
from models import db, User
from dotenv import load_dotenv
load_dotenv()


def setup_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    login_manager.login_view = 'auth.login'


def setup_cache(app):
    try:
        url = app.config.get('CACHE_REDIS_URL')
        if url:
            redis.Redis.from_url(url).ping()
        cache.init_app(app, config={
            'CACHE_TYPE': app.config.get('CACHE_TYPE', 'RedisCache'),
            'CACHE_REDIS_URL': url,
            'CACHE_DEFAULT_TIMEOUT': app.config.get('CACHE_DEFAULT_TIMEOUT', 300),
            'CACHE_IGNORE_ERRORS': True,
        })
    except redis.exceptions.ConnectionError as e:
        print(f"[Cache] Redis unavailable, falling back to SimpleCache: {e}")
        cache.init_app(app, config={
            'CACHE_TYPE': 'SimpleCache',
            'CACHE_DEFAULT_TIMEOUT': app.config.get('CACHE_DEFAULT_TIMEOUT', 300),
        })


def register_blueprints(app):
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.company import company_bp
    from routes.student import student_bp
    from routes.drives import drives_bp
    from routes.llm_chat import llm_chat_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(company_bp, url_prefix='/api/company')
    app.register_blueprint(student_bp, url_prefix='/api/student')
    app.register_blueprint(drives_bp, url_prefix='/api/drives')
    app.register_blueprint(llm_chat_bp)


def create_admin():
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        from werkzeug.security import generate_password_hash
        admin = User(
            email='admin@firstplace.local',
            password_hash=generate_password_hash('admin123'),
            role='admin',
            is_active=True
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin user created.")


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    CORS(app, supports_credentials=True, origins=[
        'http://localhost:5173',
        'http://127.0.0.1:5173',
        'http://localhost:8080',
        'http://127.0.0.1:8080',
        'https://placement-portal-2-at3j.onrender.com'
    ])

    setup_extensions(app)
    setup_cache(app)
    register_blueprints(app)

    with app.app_context():
        db.create_all()
        create_admin()

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    return app


app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
