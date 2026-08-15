# Karadeniz Sefer Planlayici

Karadeniz araştırma seferleri için Android sefer planlama uygulaması.

## Android özellikleri

- Telefonun kendi GPS'ini kullanır.
- 48 araştırma istasyonunu haritada gösterir.
- İstasyon etiketi `Proje | İstasyon Kodu` biçimindedir.
- Liman ve büyük balıkçı barınaklarının adlarını küçük etiketlerle gösterir.
- En yakın istasyona uzaklığı deniz mili (NM) olarak hesaplar.
- GPS hız bilgisi varsa en yakın istasyona ETA hesaplar.
- İstasyona 0.15 NM yaklaşıldığında varışı otomatik sefer loguna kaydeder.
- `Sefer Başlat`, `Varış`, `Hareket`, `CTD Başlat`, `CTD Tamam`, `Su Örneklemesi Tamam` olaylarını saat bilgisiyle kaydeder.
- Günlük kayıtları `sefer_log_YYYYMMDD.csv` olarak telefonun uygulama veri klasöründe tutar.

## APK derleme

`.github/workflows/build-apk.yml` GitHub Actions üzerinde debug APK üretir. `main` dalına her gönderimde ve elle `workflow_dispatch` ile çalışır.

Derleme tamamlanınca GitHub Actions çalışmasının `Artifacts` bölümünden `Karadeniz-Sefer-Planlayici-APK` indirilir.

> Bu yazılım araştırma/sefer planlaması içindir; resmi ENC/ECDIS ve seyir emniyeti araçlarının yerine geçmez.
