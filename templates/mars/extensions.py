from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Veritabanı ve Giriş Yöneticisi burada oluşturulur
db = SQLAlchemy()
login_manager = LoginManager()