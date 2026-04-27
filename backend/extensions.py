from flask_login import LoginManager
from flask_caching import Cache
from flask_mail import Mail

login_manager = LoginManager()
cache = Cache()
mail = Mail()
