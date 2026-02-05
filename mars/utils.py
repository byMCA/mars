import random
import string
from datetime import datetime

def generate_mars_id(origin_region):
    """
    Kullanıcının kökenine ve yıla göre benzersiz bir Mars Vatandaşlık ID'si üretir.
    Format: MARS-[YIL]-[BÖLGE]-[HASH]
    Örnek: MARS-2026-EU-X92F
    """
    
    # 1. Mevcut Yılı Al
    year = datetime.now().year
    
    # 2. Bölge Kodlarını Eşleştir
    # Formdan gelen 'value' değerleri ile buradakiler eşleşmelidir.
    region_map = {
        "Avrupa Federasyonu": "EU",
        "Asya Pasifik": "AP",
        "Amerika": "AM",
        "Afrika Birleşik Devletleri": "AF",
        "Diğer": "UN" # Unknown (Bilinmeyen)
    }
    
    # Gelen bölge adını koda çevir, bulamazsa 'UN' yap
    code = region_map.get(origin_region, "UN")
    
    # 3. 4 Haneli Rastgele Kriptografik Sonek Oluştur (Harf + Rakam)
    # Örn: A4K9, X1Y2 vb.
    chars = string.ascii_uppercase + string.digits
    unique_suffix = ''.join(random.choices(chars, k=4))
    
    # 4. Parçaları Birleştir
    mars_id = f"MARS-{year}-{code}-{unique_suffix}"
    
    return mars_id

# Test etmek istersen bu dosya tek başına çalıştırıldığında örnek basar
if __name__ == "__main__":
    print(generate_mars_id("Avrupa Federasyonu"))
    print(generate_mars_id("Asya Pasifik"))