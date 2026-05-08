# 🎯 Web Tabanlı Yüz Tanıma Sistemi

Menüsü web sitede olan, Flask framework ile geliştirilmiş bir yüz tanıma sistemi.

## 📋 Özellikler

✅ **Web Arayüzü** - Menü web sitede  
✅ **Yüz Kayıt** - Çoklu açılardan yüz kaydı  
✅ **Yüz Tanıma** - Kaydedilmiş yüzle giriş  
✅ **Başarılı Sayfası** - Giriş başarılı olduğunda özel sayfa  
✅ **Kullanıcı Yönetimi** - Kayıtlı kullanıcıları görüntüle ve sil  

## 🚀 Kurulum

### 1. Gerekli Paketleri Yükle

```bash
pip install -r requirements.txt
```

### 2. Uygulamayı Başlat

```bash
python app.py
```

### 3. Web Tarayıcısında Aç

```
http://localhost:5000
```

## 📸 Kullanım

### Yüz Kaydet
1. **Yeni Yüz Kaydet** linkine tıklayın
2. Adınızı girin
3. Kamera açılacak
4. **SPACE** tuşuna basarak kaydı başlatın
5. Yüzü farklı açılardan döndürün (15 saniye)
6. Otomatik olarak kaydedilir

### Yüz ile Giriş
1. **Yüz ile Giriş Yap** linkine tıklayın
2. Giriş Yap butonuna basın
3. Kamera açılacak
4. Yüzünüzü gösterin
5. Sistem tanırsa **Başarılı** sayfasına yönlendirileceksiniz

### Kayıtlı Kullanıcılar
1. **Kayıtlı Kullanıcılar** linkine tıklayın
2. Tüm kayıtlı kişileri görebilirsiniz
3. İsterseniz kişi sildebilirsiniz

## 📁 Proje Yapısı

```
proje/
├── app.py                              # Flask uygulaması
├── face_recognition_backend.py         # Yüz tanıma fonksiyonları
├── requirements.txt                    # Python bağımlılıkları
├── faces_db_enhanced.pkl              # Yüz veritabanı (otomatik oluşturulur)
└── templates/
    ├── base.html                       # Temel şablon (CSS ile)
    ├── menu.html                       # Ana menü
    ├── register.html                   # Yüz kayıt sayfası
    ├── login.html                      # Yüz giriş sayfası
    ├── success.html                    # Başarılı giriş sayfası
    └── users_list.html                 # Kullanıcı listeleme
```

## ⚙️ API Endpoints

| URL | Metod | Açıklama |
|-----|-------|----------|
| `/` | GET | Ana menü |
| `/register` | GET/POST | Yüz kayıt |
| `/login` | GET/POST | Yüz tanıma giriş |
| `/success` | GET | Başarılı giriş sayfası |
| `/users-list` | GET | Kayıtlı kullanıcılar |
| `/logout` | GET | Oturumu kapat |
| `/delete-user/<name>` | POST | Kullanıcı sil |

## 🔧 Sistem Gereksinimleri

- Python 3.7+
- Webcam/Kamera
- Windows/Linux/Mac

## 📊 Tanıma Kalitesi

- **Minimum Kare:** 15 kare
- **Kayıt Süresi:** 15 saniye
- **Giriş Süresi:** 30 saniye
- **Güven Eşiği:** 0.5 (50%)
- **Başarı Kriteri:** 3 ardışık doğru tanıma

## ⚠️ Sorun Giderme

### Kamera Açılamıyor
- Kameranın sisteme bağlı olduğundan emin olun
- Diğer uygulamaların kamerayı kullanmadığını kontrol edin

### Yüz Tanınamıyor
- Daha iyi ışıklandırma sağlayın
- Yüzü farklı açılardan kaydedin
- Kaydedilmiş yüzle benzer açıda giriş yapmayı deneyin

### Flask Başlamıyor
```bash
pip install --upgrade Flask
```

## 📝 Notlar

- Veritabanı `faces_db_enhanced.pkl` dosyasında saklanır
- Her kayıtta minimum 15 kare gereklidir
- Giriş 30 saniye sonunda otomatik başarısız olur
- SPACE ile kayıt başlatılır, Q ile iptal edilir

## 👨‍💻 Geliştirici

Bu sistem BLGM406 projesi için geliştirilmiştir.

---

**İyi Kullanımlar!** 🎉
