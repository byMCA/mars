from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

# SQLAlchemy nesnesini oluştur
db = SQLAlchemy()

# ---------------------------------------------------------
# 1. TABLO: VATANDAŞLAR (Kullanıcılar & Başvurular)
# ---------------------------------------------------------
class Citizen(UserMixin, db.Model):
    __tablename__ = 'citizen' 

    # --- KİMLİK VE GİRİŞ ---
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # --- PROFİL BİLGİLERİ ---
    full_name = db.Column(db.String(150))
    origin = db.Column(db.String(50))
    image_file = db.Column(db.String(100), nullable=False, default='default_citizen.jpg')

    # --- BİYOMETRİK VERİLER ---
    height = db.Column(db.String(10)) 
    weight = db.Column(db.String(10))
    blood_type = db.Column(db.String(10))
    
    # --- EĞİTİM VE BAŞVURU ---
    education = db.Column(db.String(100))
    specialty = db.Column(db.String(100))
    manifesto = db.Column(db.Text)
    
    # --- MARS STATÜSÜ ---
    citizenship_id = db.Column(db.String(30), unique=True, nullable=True)
    tier = db.Column(db.Integer, default=0) 
    status = db.Column(db.String(20), default="PENDING") 
    contribution_score = db.Column(db.Integer, default=0)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # --- İLİŞKİLER ---
    decrees = db.relationship('Decree', backref='author', lazy=True)
    # Report ilişkisini burada backref ile otomatik kuruyoruz (aşağıda tanımlı)

    def __repr__(self):
        return f'<Citizen {self.username} - Tier: {self.tier}>'


# ---------------------------------------------------------
# 2. TABLO: GEZEGEN DURUMU (Header Verileri)
# ---------------------------------------------------------
class PlanetaryStatus(db.Model):
    __tablename__ = 'planetary_status'

    id = db.Column(db.Integer, primary_key=True)
    sol_date = db.Column(db.Float, default=492.0)       
    oxygen_level = db.Column(db.Float, default=98.0)    
    next_transport = db.Column(db.Integer, default=14)  
    alert_level = db.Column(db.String(20), default="NORMAL")
    
    # DÜZELTME: Burası 'population_count' değil 'population' olmalı
    population = db.Column(db.Integer, default=42891) 


# ---------------------------------------------------------
# 3. TABLO: EMİRLER VE DUYURULAR
# ---------------------------------------------------------
class Decree(db.Model):
    __tablename__ = 'decrees'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    
    is_classified = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    
    # FOREIGN KEY
    author_id = db.Column(db.Integer, db.ForeignKey('citizen.id'), nullable=False)


# ---------------------------------------------------------
# 4. TABLO: RAPORLAR VE GERİ BİLDİRİMLER (DÜZELTME: Girinti silindi)
# ---------------------------------------------------------
class Report(db.Model):
    __tablename__ = 'reports'

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100), nullable=False) 
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # FOREIGN KEY
    author_id = db.Column(db.Integer, db.ForeignKey('citizen.id'), nullable=False)
    author = db.relationship('Citizen', backref='reports')

    # Bildirim Modeli
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('citizen.id'), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    category = db.Column(db.String(20), default='info') # info, warning, success, alert
    is_read = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

