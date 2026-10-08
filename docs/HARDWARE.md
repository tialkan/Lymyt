# İlk breadboard kurulumu

Hedef: Arduino Nano ESP32 + iki siyah-beyaz Waveshare 1.54 inch modül (kullanıcının kart revizyonu: 2.1). Kullanıcının verdiği [üretici sayfası](https://www.waveshare.com/wiki/1.54inch_e-Paper_Module_Manual) V1/V2 farkını açıklar. İlk firmware sürücüsü **V2 / SSD1681 varsayımıdır**; panel kimliği veya üreticinin tek ekran örneğiyle doğrulanmalıdır. Rev2.1 taşıyıcı kart yazısı tek başına kesin panel tanımlaması değildir.

Arduino IDE'de Arduino Nano ESP32 kartını ve `Tools > Pin Numbering > By Arduino pin` seç. GxEPD2, Adafruit GFX Library ve ArduinoJson 7 kütüphanelerini kur. `config.example.h` dosyasını aynı klasörde `config.h` olarak kopyala ve Wi-Fi, bilgisayarın yerel IP'si ve cihaz anahtarını gir.

## Pin planı

| Waveshare pini | Sol / Codex | Sağ / Claude |
|---|---|---|
| VCC | 3V3 | 3V3 |
| GND | GND | GND |
| DIN / MOSI | D11 | D11 |
| CLK / SCK | D13 | D13 |
| CS | D10 | D6 |
| DC | D9 | D5 |
| RST | D8 | D4 |
| BUSY | D7 | D3 |

Bu plan 3.3 V uyumlu modül varsayar; kart üzerindeki besleme şartını doğrula. GND ortaktır. `D11` Arduino pin adıdır, ESP32 `GPIO11` ile aynı değildir. D12/MISO bu ekranlarda gerekmez; ilk prototipte boş bırakılır.

İlk doğrulamayı bir ekranla yap; ikinciyi eklemeden görüntünün doğru oluştuğunu gör. `LYMYT_PARTIAL_REFRESH=false` ile firmware ekranları 3 dakikada bir tam yeniler. Gerçek panelde kısmi yenileme doğrulanınca `true` seçilebilir; bu durumda dakikada bir günceller ve her 5 kısmi yenilemeden sonra tam temizlik yapar. Bunlar başlangıç ayarlarıdır, gerçek donanımda ölçülmedi. Ekranın yüksek voltaj sürücüsü her güncellemeden sonra kapatılır.

## İsteğe bağlı ilk etkileşimler

- Basit LED: A0 → 330 Ω seri direnç → LED anot; LED katot → GND. `LYMYT_LED_PIN A0` olarak ayarla. Köprüye bağlıyken yanar; gözlenen dolu limitin yeni pencereye geçtiği doğrulanınca 12 saniye kısa yanıp sönme yapar.
- Buton: D2 → anlık buton → GND. `LYMYT_BUTTON_PIN D2` olarak ayarla. Kısa/haftalık pencereyi seçer; ekran seçimi bir sonraki izin verilen yenilemede gösterir.
- A4/A5 daha sonra I²C sensörler için ayrılabilir. A1/A2/A3 diğer etkileşimler için boştur.

Eldeki parçalar: 5 mm mavi LED'ler, ADXL345, hareket sensörü (modeli bekleniyor). Web anten ışığı mavi LED fikrini temsil eder; kasa henüz üretim çizimi değildir.

### ADXL345

VCC=3V3, GND=GND, SDA=A4, SCL=A5. Adafruit ADXL345 ve Unified Sensor kütüphanelerini ekle, `LYMYT_USE_ADXL345=true` seç. Varsayılan adres 0x53; alternatif adresli kartta 0x1D olabilir. CS/SDO pinleri dışarı verilen kartlarda I²C için CS=3V3, SDO=GND (0x53) gerekir; modül pinlerini doğrula.

Firmware 10 Hz'de ivme okur, eğime göre bakış yönünü ayarlar. İvmenin büyüklüğü 1g'den 3 m/s² fazla değişince LED tepki verir. Eşik fiziksel kasada ayarlanmalı. Bakış bir sonraki izin verilen e-paper yenilemesinde değişir. X/Y/Z değerleri yardımcının telemetrisine gönderilir.

### Hareket sensörü

Model netleşene kadar besleme kablosunu bağlama. Sinyal çıkışı 3.3 V uyumluysa OUT=A1, GND=GND ve `LYMYT_MOTION_PIN=A1` seçilir. HIGH hareket sayılır. Yeni hareket LED tepkisi verir; 5 dakika hareket yoksa gözler bir sonraki yenilemede uyur. PIR, hareketsiz oturan kişinin varlığını güvenilir biçimde saptamaz.

İlk kurulum bir mavi LED kullanır. Çoklu LED'ler GPIO'ya doğrudan bağlanmaz; ışık grubu için sürücü transistörü/MOSFET ve her LED için seri direnç gerekir.

## Karakter planı

Her göz kendi kapasitesine tepki verir: %20'nin üzerinde açık göz, %1–20 mahmur, %0 kapalı göz. Güncel veri yoksa küçük nötr göz ve son bilinen bilgi gösterir. Geri sayımın bitmesi doğrulama bekleme durumudur; bilgisayardan yeni limit penceresi gelmeden kapasite dolu kabul edilmez. Gelecekte dokunma kısa bir sevinç, yaklaşma bakış yönü, ortam ışığı gece modu ve LED bir ruh hali ışığı sağlayabilir.

## Güç

İlk prototip USB-C ile beslenecek. Veri Wi-Fi üzerinden gelir. Kablosuz veri bağlantısı cihazı elektrik açısından kablosuz yapmaz; pil, şarj devresi ve düşük güç ayarları ikinci aşamadır.
