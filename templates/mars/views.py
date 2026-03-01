from django.shortcuts import render
from django.contrib.auth.models import User # Django'nun kullanıcı modeli
from .models import Duyuru

# Ana Sayfa View'ı
def ana_sayfa(request):
    # 1. Kayıtlı Kullanıcı Sayısını Al (Dinamik Nüfus)
    toplam_nufus = User.objects.count() 
    
    # 2. Sadece Başlıklar için Son 5 Duyuruyu Al
    haberler = Duyuru.objects.filter(aktif_mi=True)[:5] 

    context = {
        'toplam_nufus': toplam_nufus,
        'haberler': haberler
    }
    return render(request, 'ana_sayfa.html', context)

# Duyurular Sayfası View'ı
def duyurular(request):
    tum_duyurular = Duyuru.objects.filter(aktif_mi=True)
    return render(request, 'duyurular.html', {'duyurular': tum_duyurular})