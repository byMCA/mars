import os
import random
import string
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import base64
import time
from flask import Flask, render_template, request, redirect, url_for, flash, abort, jsonify 
from sqlalchemy import or_
from models import db, Citizen, PlanetaryStatus, Decree, Report, Notification

# ==========================================
# 1. UYGULAMA VE VERİTABANI AYARLARI
# ==========================================
app = Flask(__name__)
app.config['SECRET_KEY'] = 'mars_mission_2030_secure_key_alpha' 

# Veritabanı Yolu Ayarı
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'mars_core.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_BINDS'] = {
    'forum': 'sqlite:///forum.db'  # İkinci veritabanı
}

# Eklentileri Başlat
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' 

# ==========================================
# 2. SABİTLER VE YARDIMCI FONKSİYONLAR
# ==========================================

TIER_NAMES = {
    0: "Aday (Applicant)",
    1: "Vatandaş (Citizen)",
    2: "Kıdemli Vatandaş (Senior)",
    3: "Uzman (Specialist)",
    4: "Öncü (Vanguard)",
    5: "Tekmokrat (Technocrat)",
    6: "Mühendis (Engineer)",
    7: "Bilim İnsanı (Scientist)",
    8: "Operatör (Operator)",
    9: "Gözetmen (Overseer)", 
    10: "Koloni Mimarı (Architect)",
    11: "Yıldız Gezgini (Star Walker)",
    12: "Yüksek Konsey (High Council)",
    13: "Gezegen Savunucusu (Defender)",
    14: "Diplomat",
    15: "Galaktik Elçi (Galactic Ambassador)",
    16: "Terraform Mimarı",
    17: "Sistem Lordu (System Lord)",
    18: "Yüce Hükümdar (Grand Ruler)",
    19: "Ölümsüz (Eternal)",
    20: "Mars İmparatoru (Imperator)"
}

@app.context_processor
def inject_tiers():
    return dict(tier_names=TIER_NAMES)

def generate_mars_id(origin):
    """
    Onaylanan vatandaşlar için ID üretir
    """
    origin_code = origin[:2].upper() if origin else "UN"
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"MARS-4320-{origin_code}-{suffix}"

@login_manager.user_loader
def load_user(user_id):
    return Citizen.query.get(int(user_id))

# ==========================================
# 3. İLK KURULUM FONKSİYONU
# ==========================================
def create_initial_data():
    with app.app_context():
        db.create_all()
        
        # 1. Gezegen Durumu
        if not PlanetaryStatus.query.first():
            status = PlanetaryStatus(
                sol_date=492.4,
                oxygen_level=98.2,
                next_transport=14,
                alert_level="NORMAL",
                population=1
            )
            db.session.add(status)
            db.session.commit()
            print(">> SİSTEM: Gezegen durumu başlatıldı.")

        if not Citizen.query.filter_by(username='admin').first():
            admin = Citizen(
                username='admin',
                email='admin@mars.gov',
                password_hash=generate_password_hash('mars123', method='pbkdf2:sha256'),
                full_name='System Commander',
                origin='Earth-HQ',
                citizenship_id='MARS-CMD-001',
                tier=20, 
                status='APPROVED',
                manifesto='System Administrator',
                education='PhD Astro-Physics',
                specialty='Command & Control'
            )
            db.session.add(admin)
            db.session.commit()
            print(">> SİSTEM: Admin oluşturuldu (User: admin / Pass: mars123)")

create_initial_data()

@app.context_processor
def inject_notifications():
    if current_user.is_authenticated:
        # Okunmamış mesaj sayısı
        unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
        return dict(unread_count=unread_count)
    return dict(unread_count=0)

# ==========================================
# 4. GENEL ROTALAR (PUBLIC ROUTES)
# ==========================================

@app.route('/')
def index():
    # 1. Gezegen Durumunu Çek
    durum = PlanetaryStatus.query.first()
    
    # Eğer veritabanı boşsa varsayılan oluştur
    if not durum: 
        durum = PlanetaryStatus(population=0, oxygen_level=98.2, alert_level="NORMAL")
        db.session.add(durum)
        db.session.commit()

    # 2. CANLI NÜFUS HESAPLAMA (GÜNCELLENDİ)
    # Onaylı vatandaşları say
    onayli_sayisi = Citizen.query.filter_by(status='APPROVED').count()
    
    # Bekleyenleri say
    bekleyen_sayisi = Citizen.query.filter_by(status='PENDING').count()
    
    # HİKAYE: 142 Kurucu + Onaylı Vatandaşlar + Bekleyenler (Adaylar da nüfus sayılır)
    # İstersen sadece onaylıları saymak için '+ bekleyen_sayisi' kısmını sil.
    yeni_nufus = 280 + onayli_sayisi 
    
    # Durumu güncelle
    durum.population = yeni_nufus
    
    # Değişikliği veritabanına işle
    db.session.add(durum)
    db.session.commit()
    
    # Konsola bilgi bas (Terminale bakarak kontrol edebilirsin)
    print(f">> NÜFUS GÜNCELLENDİ: Taban(142) + Onaylı({onayli_sayisi}) = {yeni_nufus}")

    # 3. Diğer Verileri Çek
    decrees = Decree.query.order_by(Decree.date_posted.desc()).limit(10).all()
    weekly_citizen = Citizen.query.filter(Citizen.tier < 20).order_by(Citizen.contribution_score.desc()).first()

    return render_template('index.html', durum=durum, decrees=decrees, weekly_citizen=weekly_citizen)


@app.route('/apply', methods=['GET', 'POST'])
def apply():
    if request.method == 'POST':
        durum = PlanetaryStatus.query.first()
        # --- KİMLİK BİLGİLERİ ---
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        full_name = request.form.get('full_name')
        password = request.form.get('password')
        origin = request.form.get('origin')
        
        # --- BİYOMETRİK BİLGİLER (YENİ: Formdan alınıyor) ---
        height = request.form.get('height')
        weight = request.form.get('weight')
        blood_type = request.form.get('blood_type')
        
        # --- TEKNİK BİLGİLER ---
        education = request.form.get('education')
        specialty = request.form.get('specialty')
        manifesto = request.form.get('manifesto')
        image_data = request.form.get('image_data')

        # 1. Benzersizlik Kontrolleri
        existing_user = Citizen.query.filter_by(username=username).first()
        if existing_user:
            flash(f'HATA: "{username}" kod adı zaten sistemde kayıtlı.', 'error')
            return redirect(url_for('apply'))
            
        if Citizen.query.filter_by(email=email).first():
            flash('HATA: Bu E-Mail adresi zaten kullanımda.', 'error')
            return redirect(url_for('apply'))

        # 2. Fotoğraf İşleme
        image_filename = 'default_citizen.jpg'
        if image_data and "base64," in image_data:
            try:
                base64_data = image_data.split(",")[1]
                timestamp = str(int(time.time()))
                image_filename = f"{username}_{timestamp}.jpg"
                
                upload_folder = os.path.join(app.root_path, 'static/profile_pics')
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)
                    
                file_path = os.path.join(upload_folder, image_filename)
                with open(file_path, "wb") as fh:
                    fh.write(base64.b64decode(base64_data))
            except Exception as e:
                print(f"Fotoğraf Hatası: {e}")

        # 3. Veritabanına Kayıt
        new_citizen = Citizen(
            username=username,
            email=email,
            full_name=full_name,
            password_hash=generate_password_hash(password, method='pbkdf2:sha256'),
            origin=origin,
            
            # Artık rastgele değil, kullanıcının girdiği veriler:
            height=height,
            weight=weight,
            blood_type=blood_type,
            
            education=education,
            specialty=specialty,
            manifesto=manifesto,
            image_file=image_filename,
            tier=0,            
            status='PENDING'   
        )

        try:
            db.session.add(new_citizen)
            db.session.commit()
            flash('Başvurunuz sisteme işlendi. Konsey onayı bekleniyor.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            print(f"Veritabanı Hatası: {e}")
            flash('Sistem hatası oluştu.', 'error')

    return render_template('apply.html')

# --- YENİ VATANDAŞ YÖNETİM SAYFASI ---
@app.route('/admin/citizens', methods=['GET'])
@login_required
def admin_citizens():
    if current_user.tier <= 18:
        return redirect(url_for('dashboard'))

    # Arama Parametresi
    q = request.args.get('q')
    
    query = Citizen.query.filter(Citizen.status != 'PENDING') # Bekleyenleri alma

    if q:
        # İsimde, Kullanıcı adında veya ID'de arama yap
        search = f"%{q}%"
        query = query.filter(
            or_(
                Citizen.username.like(search),
                Citizen.full_name.like(search),
                Citizen.citizenship_id.like(search)
            )
        )

    # Rütbeye göre sırala (En yüksek rütbe en üstte)
    citizens = query.order_by(Citizen.tier.desc()).all()
    
    return render_template('admin_citizens.html', citizens=citizens, search_query=q)

# --- BANLAMA FONKSİYONU ---
@app.route('/admin/ban_user/<int:user_id>')
@login_required
def ban_user(user_id):
    if current_user.tier <= 18: abort(403)
    
    user = Citizen.query.get_or_404(user_id)
    
    # İmparator kendini banlayamaz :)
    if user.tier >= 20:
        flash('İmparator sistemden yasaklanamaz.', 'error')
        return redirect(url_for('admin_citizens'))

    user.status = 'BANNED'
    user.tier = 0 # Rütbesini sök
    db.session.commit()
    
    flash(f'{user.username} koloniden sürgün edildi (BANLANDI).', 'success')
    return redirect(url_for('admin_citizens'))

# --- BAN KALDIRMA ---
@app.route('/admin/unban_user/<int:user_id>')
@login_required
def unban_user(user_id):
    if current_user.tier <= 18: abort(403)
    
    user = Citizen.query.get_or_404(user_id)
    user.status = 'APPROVED'
    user.tier = 1 # Vatandaş olarak geri al
    db.session.commit()
    
    flash(f'{user.username} yasağı kaldırıldı.', 'success')
    return redirect(url_for('admin_citizens'))

# --- MESAJ GÖNDERME (SİMÜLASYON) ---
@app.route('/admin/message_user', methods=['POST'])
@login_required
def message_user():
    if current_user.tier <= 18: abort(403)
    
    user_id = request.form.get('user_id')
    message = request.form.get('message')
    
    # Veritabanına Kaydet
    new_notif = Notification(user_id=user_id, message=message, category='warning')
    db.session.add(new_notif)
    db.session.commit()
    
    flash('Mesaj şifreli ağ üzerinden iletildi.', 'success')
    return redirect(url_for('admin_citizens'))

@app.route('/notifications')
@login_required
def notifications():
    # Kullanıcının bildirimlerini çek (En yeniden eskiye)
    user_notifs = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.timestamp.desc()).all()
    
    # Hepsini okundu işaretle
    for notif in user_notifs:
        notif.is_read = True
    db.session.commit()
    
    return render_template('notifications.html', notifications=user_notifs)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = Citizen.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            if user.status == 'APPROVED':
                login_user(user)
                # Admin ise panele, değilse dashboard'a
                if user.tier >= 9:
                    return redirect(url_for('admin_panel'))
                return redirect(url_for('dashboard'))
            
            elif user.status == 'PENDING':
                flash('Giriş başarısız: Başvurunuz hala inceleme aşamasında.', 'warning')
            elif user.status == 'REJECTED':
                flash('Giriş engellendi: Başvurunuz reddedildi.', 'error')
        else:
            flash('Hatalı kullanıcı adı veya parola.', 'error')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Oturum kapatıldı.', 'success')
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)


@app.route('/duyurular')
def duyurular():
    decrees = Decree.query.filter_by(is_active=True).order_by(Decree.date_posted.desc()).all()
    return render_template('duyurular.html', duyurular=decrees)


@app.route('/duyuru/<int:id>')
def duyuru_detay(id):
    decree = Decree.query.get_or_404(id)
    if decree.is_classified and (not current_user.is_authenticated or current_user.tier < 1):
        flash('Bu belgeye erişim yetkiniz yok (Sınıflandırılmış İçerik).', 'error')
        return redirect(url_for('index'))

    return render_template('duyuru_detay.html', decree=decree)


# ==========================================
# 5. YÖNETİM PANELİ (ADMIN ROUTES)
# ==========================================

@app.route('/admin')
@login_required
def admin_panel():
    # 1. Yetki Kontrolü
    if current_user.tier <= 18:
        flash('YETKİSİZ ERİŞİM!', 'error')
        return redirect(url_for('dashboard'))

    # 2. Bekleyen Başvuruları Çek
    pending_users = Citizen.query.filter_by(status='PENDING').order_by(Citizen.timestamp.desc()).all()
    
    # --- BU SATIR EKSİK OLABİLİR: Onaylı Vatandaşları Çek ---
    approved_users = Citizen.query.filter_by(status='APPROVED').order_by(Citizen.tier.desc()).all()
    # --------------------------------------------------------

    decrees = Decree.query.order_by(Decree.date_posted.desc()).all()
    reports = Report.query.order_by(Report.timestamp.desc()).all()
    
    durum = PlanetaryStatus.query.first() 
    if not durum: 
        durum = PlanetaryStatus(alert_level="NORMAL")

    # 3. Şablonu Render Et (approved_users EKLENDİ Mİ DİKKAT ET)
    return render_template('admin_panel.html', 
                         pending_users=pending_users, 
                         approved_users=approved_users,  # <--- BURASI MUTLAKA OLMALI
                         decrees=decrees, 
                         reports=reports, 
                         durum=durum)



# --- Rütbe Güncelleme (SADECE TIER 20) ---
@app.route('/admin/update_rank', methods=['POST'])
@login_required
def update_rank():
    # GÜVENLİK DUVARI: Sadece Tier 20 (İmparator) rütbe değiştirebilir.
    if current_user.tier != 20:
        flash('ERİŞİM REDDEDİLDİ: Rütbe atama yetkisi sadece Mars İmparatoruna aittir!', 'error')
        return redirect(url_for('admin_panel'))
    
    user_id = request.form.get('user_id')
    new_tier = request.form.get('new_tier')
    
    user = Citizen.query.get(user_id)
    if user:
        if user.id == current_user.id:
             flash('Kendi rütbenizi değiştiremezsiniz İmparatorum.', 'warning')
             return redirect(url_for('admin_panel'))

        user.tier = int(new_tier)
        db.session.commit()
        
        rank_name = TIER_NAMES.get(int(new_tier), "Bilinmeyen")
        flash(f"{user.username} kullanıcısının rütbesi güncellendi: {rank_name}", "success")
        
    return redirect(url_for('admin_panel'))


@app.route('/admin/approve/<int:user_id>')
@login_required
def approve_user(user_id):
    if current_user.tier <= 18:
        abort(403)

    user = Citizen.query.get_or_404(user_id)
    user.status = 'APPROVED'
    user.tier = 1 
    user.citizenship_id = generate_mars_id(user.origin)
    
    db.session.commit()
    flash(f'{user.full_name} vatandaşlığa kabul edildi. ID: {user.citizenship_id}', 'success')
    return redirect(url_for('admin_panel'))


@app.route('/admin/reject/<int:user_id>')
@login_required
def reject_user(user_id):
    if current_user.tier <= 18:
        abort(403)

    user = Citizen.query.get_or_404(user_id)
    user.status = 'REJECTED'
    
    db.session.commit()
    flash(f'{user.full_name} başvurusu reddedildi.', 'warning')
    return redirect(url_for('admin_panel'))


@app.route('/admin/add_decree', methods=['POST'])
@login_required
def add_decree():
    if current_user.tier <= 18:
        abort(403)

    title = request.form.get('title')
    content = request.form.get('content')
    is_classified = True if request.form.get('is_classified') else False

    if title and content:
        new_decree = Decree(
            title=title,
            content=content,
            is_classified=is_classified,
            author_id=current_user.id,
            is_active=True
        )
        db.session.add(new_decree)
        db.session.commit()
        flash('Yeni gezegen emri başarıyla yayınlandı.', 'success')
    else:
        flash('Hata: Başlık ve içerik zorunludur.', 'error')

    return redirect(url_for('admin_panel'))


@app.route('/admin/delete_decree/<int:id>')  
@login_required
def delete_decree(id):                     
    if current_user.tier <= 18:
        abort(403)
        
    decree = Decree.query.get_or_404(id)     
    db.session.delete(decree)
    db.session.commit()
    
    flash('Duyuru arşivden silindi.', 'warning')
    return redirect(url_for('admin_panel'))

@app.route('/check_username', methods=['POST'])
def check_username():
    data = request.get_json()
    # strip() ekleyerek boşlukları siliyoruz
    username = data.get('username', '').strip() 
    
    if not username:
        return jsonify({'available': False, 'message': 'Boş bırakılamaz.'})

    # Veritabanında ararken de temizlenmiş haliyle arıyoruz
    user = Citizen.query.filter_by(username=username).first()
    
    if user:
        return jsonify({'available': False, 'message': 'KOD ADI KULLANIMDA (MEVCUT)'})
    else:
        return jsonify({'available': True, 'message': 'KOD ADI MÜSAİT'})
    
    # --- KİMLİK FOTOĞRAFI YÜKLEME (TEK SEFERLİK) ---
@app.route('/upload_id_photo', methods=['POST'])
@login_required
def upload_id_photo():
    # Güvenlik Kontrolü: Fotoğraf daha önce değiştirilmişse işlemi durdur
    if current_user.image_file != 'default_citizen.jpg':
        flash('ERİŞİM REDDEDİLDİ: Kimlik fotoğrafı onaylanmış ve kilitlenmiştir. Değiştirilemez.', 'error')
        return redirect(url_for('dashboard'))

    if 'photo' not in request.files:
        flash('Dosya bulunamadı.', 'error')
        return redirect(url_for('dashboard'))
    
    file = request.files['photo']
    
    if file.filename == '':
        flash('Seçili dosya yok.', 'error')
        return redirect(url_for('dashboard'))

    if file:
        try:
            # Dosya ismini güvenli hale getir ve benzersiz yap
            file_ext = os.path.splitext(file.filename)[1] # .jpg, .png vs.
            timestamp = str(int(time.time()))
            new_filename = f"{current_user.username}_ID_{timestamp}{file_ext}"
            
            # Kaydetme yolu
            upload_folder = os.path.join(app.root_path, 'static/profile_pics')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            
            file_path = os.path.join(upload_folder, new_filename)
            file.save(file_path)
            
            # Veritabanını güncelle
            current_user.image_file = new_filename
            db.session.commit()
            
            flash('Kimlik fotoğrafı işlendi ve biometrik çipe kilitlendi.', 'success')
        except Exception as e:
            print(f"Hata: {e}")
            flash('Yükleme sırasında teknik bir hata oluştu.', 'error')

    return redirect(url_for('dashboard'))
# --- BUTON İŞLEVLERİ (İNDİRME VE RAPORLAMA) ---

@app.route('/download_id_data')
@login_required
def download_id_data():
    # 1. Havalı bir dijital dosya içeriği oluştur
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    secure_hash = generate_password_hash(current_user.username)[-20:].upper()
    
    file_content = f"""
    =============================================================
    MARS COLONIZATION AUTHORITY - OFFICIAL CITIZEN DOSSIER
    =============================================================
    SECURE DATA EXPORT // TIMESTAMP: {timestamp}
    ENCRYPTION LEVEL: QUANTUM-7 // HASH: {secure_hash}
    =============================================================

    [ PERSONAL IDENTITY ]
    ---------------------
    CITIZEN ID   : {current_user.citizenship_id}
    CODENAME     : {current_user.username}
    FULL NAME    : {current_user.full_name}
    ORIGIN       : {current_user.origin}
    
    [ BIOMETRIC DATA ]
    ------------------
    HEIGHT       : {current_user.height} cm
    WEIGHT       : {current_user.weight} kg
    BLOOD TYPE   : {current_user.blood_type}
    GENETIC HASH : {generate_password_hash(current_user.username)}

    [ COLONY STATUS ]
    -----------------
    TIER LEVEL   : {current_user.tier}
    CONTRIBUTION : {current_user.contribution_score} XP
    STATUS       : {current_user.status}
    SPECIALTY    : {current_user.specialty}

    [ MANIFESTO ]
    -------------
    "{current_user.manifesto}"

    =============================================================
    WARNING: THIS DOCUMENT IS PROPERTY OF MARS GOV.
    UNAUTHORIZED DUPLICATION IS A CLASS-A FELONY.
    =============================================================
    """
    
    # 2. Dosyayı kullanıcıya "indirilebilir" olarak sun
    from flask import Response
    return Response(
        file_content,
        mimetype="text/plain",
        headers={"Content-Disposition": f"attachment;filename=MARS_ID_{current_user.username}.txt"}
    )

@app.route('/send_status_report', methods=['POST'])
@login_required
def send_status_report():
    category = request.form.get('category') # Select'ten gelen veri
    feedback = request.form.get('feedback_text')
    
    # Veritabanına Kayıt
    new_report = Report(
        category=category,
        content=feedback,
        author_id=current_user.id
    )
    
    db.session.add(new_report)
    db.session.commit()
    
    flash(f'İLETİM BAŞARILI: Raporunuz şifrelendi ve Yüksek Konsey sunucularına işlendi.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/admin/delete_report/<int:report_id>')
@login_required
def delete_report(report_id):
    if current_user.tier <= 18:
        abort(403)
        
    report = Report.query.get_or_404(report_id)
    db.session.delete(report)
    db.session.commit()
    flash('Rapor arşivden silindi.', 'success')
    return redirect(url_for('admin_panel'))


@app.route('/forum')
@login_required
def forum():
    # Şimdilik sadece boş bir şablon döndürüyoruz
    return render_template('forum.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)