from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask import redirect, url_for, flash

# Modellerini import et (dosya adın model.py ise ona göre düzenle)
from models import db, Citizen, Decree, PlanetaryStatus, ForumThread

# ---------------------------------------------------------
# 1. GÜVENLİK AYARLARI (Sadece Tier 9 - Adminler Girebilsin)
# ---------------------------------------------------------
class SecureModelView(ModelView):
    def is_accessible(self):
        # Kullanıcı giriş yapmış mı VE Tier seviyesi 9 mu?
        return current_user.is_authenticated and current_user.tier == 9

    def inaccessible_callback(self, name, **kwargs):
        # Yetkisi yoksa giriş sayfasına at
        flash("Bu alana erişim yetkiniz yok!", "danger")
        return redirect(url_for('login'))

class SecureIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.tier == 9

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

# ---------------------------------------------------------
# 2. VATANDAŞLAR (Citizen) YÖNETİMİ
# ---------------------------------------------------------
class CitizenAdmin(SecureModelView):
    # Listede görünecek sütunlar
    column_list = ('username', 'full_name', 'tier', 'status', 'origin', 'citizenship_id', 'contribution_score')
    
    # Arama yapılabilecek alanlar
    column_searchable_list = ['username', 'full_name', 'citizenship_id']
    
    # Yan taraftaki filtreler
    column_filters = ['tier', 'status', 'origin', 'blood_type']
    
    # Düzenleme formunda görünecek alanlar (Password hash'i gizledik)
    form_columns = ('username', 'full_name', 'origin', 'tier', 'status', 'citizenship_id', 
                    'education', 'specialty', 'height', 'weight', 'blood_type', 'contribution_score', 'image_file')

    # Status alanını Dropdown (seçenekli) yapalım
    form_choices = {
        'status': [
            ('PENDING', 'Beklemede'),
            ('APPROVED', 'Onaylandı'),
            ('REJECTED', 'Reddedildi')
        ]
    }
    
    can_export = True  # Verileri Excel/CSV olarak indirme izni

# ---------------------------------------------------------
# 3. HABERLER VE EMİRLER (Decree) YÖNETİMİ
# ---------------------------------------------------------
class DecreeAdmin(SecureModelView):
    column_list = ('title', 'author', 'is_active', 'is_classified', 'date_posted')
    column_searchable_list = ['title', 'content']
    column_filters = ['is_active', 'is_classified', 'date_posted']
    
    # Formda yazar seçerken sadece ID yerine kullanıcı adını gösterir
    column_labels = dict(author='Yayınlayan Admin')

# ---------------------------------------------------------
# 4. GEZEGEN DURUMU (Planetary Status) YÖNETİMİ
# ---------------------------------------------------------
class PlanetAdmin(SecureModelView):
    # Bu tablodan yeni kayıt eklenmesini engelleyebilirsin (Sadece var olanı düzenle)
    can_create = False 
    can_delete = False
    
    column_list = ('sol_date', 'oxygen_level', 'next_transport', 'alert_level', 'population_count')

# ---------------------------------------------------------
# 5. KURULUM FONKSİYONU (App.py'da çağırılacak)
# ---------------------------------------------------------
def init_admin(app):
    # Admin panelini başlat
    admin = Admin(app, name='Mars Koloni Paneli', template_mode='bootstrap4', index_view=SecureIndexView())

    # Modelleri panele ekle
    admin.add_view(CitizenAdmin(Citizen, db.session, name="Vatandaşlar"))
    admin.add_view(DecreeAdmin(Decree, db.session, name="Duyurular & Emirler"))
    admin.add_view(PlanetAdmin(PlanetaryStatus, db.session, name="Gezegen Durumu"))
    # Forum başlıklarını standart görünümle ekle
    admin.add_view(SecureModelView(ForumThread, db.session, name="Forum Konuları"))

    return admin