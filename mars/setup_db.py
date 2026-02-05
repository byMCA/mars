from app import app, db, Citizen, Report, PlanetaryStatus, Decree
from werkzeug.security import generate_password_hash
from datetime import datetime

with app.app_context():
    # Eski tabloları sil ve yenisini oluştur (Temiz Kurulum)
    db.drop_all()
    db.create_all()
    print(">> Veritabanı sıfırlandı ve yeniden oluşturuldu.")

    # 2. BEKLEYEN BAŞVURU (User 1)
    user1 = Citizen(
        username='ASTRO_AHMET',
        email='ahmet@mail.com', # Mail eklendi
        full_name='Ahmet Yılmaz',
        password_hash=generate_password_hash('123'),
        origin='EU', height=175, weight=70, blood_type='0+',
        education='Mühendis', specialty='Botanik',
        manifesto='Patates yetiştirmek istiyorum.',
        tier=1, status='PENDING', image_file='default_citizen.jpg'
    )

    # 3. BEKLEYEN BAŞVURU (User 2)
    user2 = Citizen(
        username='SPACE_AYSE',
        email='ayse@mail.com', # Mail eklendi
        full_name='Ayşe Demir',
        password_hash=generate_password_hash('123'),
        origin='AS', height=165, weight=55, blood_type='B+',
        education='Doktor', specialty='Cerrahi',
        manifesto='İnsan hayatını korumaya geliyorum.',
        tier=2, status='PENDING', image_file='default_citizen.jpg'
    )

    # 4. KOLONİ DURUMU (NÜFUS BURADA)
    durum = PlanetaryStatus(alert_level='YELLOW', oxygen_level=94, population=142)

    db.session.add(user1)
    db.session.add(user2)
    db.session.add(durum)
    db.session.commit()

    # 5. RAPORLAR
    rapor1 = Report(
        category='Teknik Arıza',
        content='Su arıtma tesisinde 3. pompa ses yapıyor. Acil bakım gerek.',
        author_id=user1.id, timestamp=datetime.utcnow()
    )
    rapor2 = Report(
        category='İstihbarat',
        content='Kuzey sektöründe tanımlanamayan sismik aktiviteler tespit edildi.',
        author_id=user2.id, timestamp=datetime.utcnow()
    )

    db.session.add(rapor1)
    db.session.add(rapor2)
    db.session.commit()

    print(">> TEST VERİLERİ YÜKLENDİ: Nüfus, Başvurular ve Raporlar hazır.")
    print(">> GİRİŞ BİLGİSİ: Kullanıcı Adı: CEMAL_PASA / Şifre: 123456")