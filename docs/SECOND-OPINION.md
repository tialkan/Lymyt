# Lymyt için bağımsız tasarım incelemesi

Aşağıdaki promptu istediğin LLM'e ver; cevabını bu sohbete getir. Hesap anahtarı, Wi-Fi şifresi veya kişisel kullanım verisi ekleme.

```text
Lymyt adlı, Arduino Nano ESP32 tabanlı bir masa arkadaşının tasarımını bağımsız incele. Genel övgü yerine hataları, eksik ölçümleri ve uygulanabilir düzeltmeleri bul. Varsayımları gerçeklerden ayır; elektrik ve ekran önerilerini üreticinin güncel belgeleriyle doğrula.

Donanım: Arduino Nano ESP32, iki Waveshare 1.54 inç siyah-beyaz e-paper modülü, taşıyıcı kart Rev2.1. Rev2.1 panel sürücüsünü kesinleştirmiyor; GxEPD2_154_D67 şimdilik aday. Nano'nun headerları henüz lehimlenmedi; iki ekran fiziksel testte beyaz. Mavi onboard LED ve USB yüklemesi çalışıyor. ADXL345 ve modeli henüz bilinmeyen hareket sensörü elde var, bağlı değil. Güncel sürümde harici LED kullanılmıyor. Alternatif kart: fotoğrafta pinleri lehimli, USB girişli klasik 30 pin ESP32-WROOM; henüz bu kartta görünür ekran testi yapılmadı.

E-paper bağlantısı: ortak VCC=3V3, GND, DIN=D11, CLK=D13. Sol CS/DC/RST/BUSY=D10/D9/D8/D7. Sağ=D6/D5/D4/D3. LED kapalı (-1), buton=D2-GND INPUT_PULLUP, hareket=A1. ADXL345 SDA=A4 SCL=A5, 3V3, adres0x53; kartta varsa CS=3V3 SDO=GND. Arduino pin numaralandırması seçiliyor; GPIO numaralarıyla karıştırılmıyor.

WROOM e-paper: ortak MOSI23/SCK18, 3V3/GND; sol CS27/DC26/RST25/BUSY34; sağ CS33/DC32/RST14/BUSY35. Kart breadboard dışında; bir GPIO pininden tek kablo, aynı a–e şeridinden iki ekrana dağıtım. WROOM buton4-GND; OLED sol SDA21/SCL22, sağ SDA16/SCL17. Nano pin adları ile klasik ESP32 GPIO numaraları karıştırılmıyor.

Ucuz alternatif: iki 0.96 inç 128×64 SSD1306 I2C OLED. İkisi de 0x3C olabileceği için sol SDA=A4/SCL=A5, sağ SDA=A2/SCL=A3; ESP32'nin iki ayrı donanım I2C hattı. Her iki ekrana 3V3. SSD1306 ile SH1106/SPI seçenekleri eşdeğer kabul edilmiyor. Türkçe Unicode font ve satır kırma gerekli.

İşlev: sol Codex, sağ Claude Code kalan yüzde ve reset süresi; bilinmeyen veri sıfır olarak gösterilmiyor, eski veri 'son bilinen'. Limit modundan bir basış C1 kelimeye geçiyor: solda İngilizce, sağda Türkçe. Kelimeden bir basış 'öğrendim' kaydedip limit moduna dönüyor; sonraki basış sonraki kelime. Debounce40ms, güç kesilince ilerleme NVS'de. E-paper varsayılan tam yenileme180sn, sadece gerçek panelde doğrulandıktan sonra kısmi60sn. Bekleyen yenilemede ekstra basışlar görünmeyen kelimeleri atlamıyor. OLED hemen geçiyor. Bu etkileşimin e-paper sınırlamaları için daha iyi, panel ömrünü koruyan tasarım önerebilir misin?

Veri: bilgisayarda salt okunur Codex app-server account/rateLimits/read; Claude resmî statusline rate_limits, plan/oturum kısıtları mevcut. Team hesabında alan gelmeyebilir. Web kullanım ekranından elle alınan değer ayrı kaynakla işaretleniyor ve eskime zamanı korunuyor. USB115200 NDJSON ya da Wi-Fi yerel yardımcı/VPS relay. Tokenlar ve hesap oturumları public rehbere gitmiyor. Bilgisayar kapalıyken kelimeler offline; kota otomatik ölçülemez.

Kalıcı devre: breadboarddan sonra 50×100mm yalıtılmış pedli delikli bakır pertinaks, Nano2×15 dişi soket; düz kesintisiz bakır levhaya doğrudan lehim yok. İki ekran sökülebilir kablolu. 3D gövde ölçü denemesi150×100×55mm, duvar2.4mm, arka kapak2.4mm, iki34×34mm göz açıklığı. Pil yuvası için70×70×25mm hacim bütçesi,100×50mm plaket ayrı derinlikte; büyük830delikli breadboard dahil değil. Kablo payı≥8mm. Panel camına/şerit kablosuna basınç uygulanmaz. USB yan açıklığı20×14mm; gerçek soket konumu ölçülmeli. İç parça sabitlemeleri prototipte ayarlanmalı. Kapak4M3 vida/somunla sökülebilir. Önce60×44mm uyum test parçası basılacak. STL manifoldluğu yazılımla kontrol edildi, fiziksel baskı henüz yok.

Güç: tercihen4×1.2V eş NiMH AA, haricî NiMH şarj cihazı. Pil→anahtar→düşük gerilim korumalı5V buck-boost→Nano USB-C. Yaklaşık4–6V giriş aralığında en az1A sürekli çıkış ve Wi-Fi pikleri doğrulanmalı. VIN'e4AA doğrudan bağlanmıyor; Nano pilleri şarj etmez. Somut regülatör modeli, hücre kesme eşiği ve çalışma süresi henüz ölçülmedi.

Yayın: tezatlas.com/lymyt, mevcut TezAtlas Next.js temasında 'Sıfırdan tasarım' rehberi. Seçenekli Robotistan örnek sepet, adım adım breadboard/lehimli plaket görselleri, pin tablosu, gerçek sürücü ayrımı, gövde STL/SCAD dosyaları, kaynak kod indirme. Fiyatlar tarihli yaklaşık; ürün stokları ve satın alma satıcıda. Public önizleme gerçek hesap limitleri değil örnek veriler.

Şu formatta yanıtla:
1. En kritik 5 sorun: önem, gerekçe, somut düzeltme ve birincil kaynak.
2. Pin çakışmaları, I2C hatları, seviye uyumu, reset/BUSY ve OLED adresleri için bağlantı incelemesi.
3. NiMH güç tasarımı: uygun regülatör özellikleri, hücre dengesizliği, kesme ve tahmini enerji hesabı. Ölçülmemiş tüketimi varsayım diye belirt.
4. 3D gövde: kritik ölçüler, modül/kablo/USB ve pil servis erişimi, baskı yönü, montaj ve tolerans. 'Kesin sığar' demeden eksik ölçüleri belirt.
5. Kelime öğrenme etkileşimi: öğrendim ve tekrar arasındaki fark, offline ilerleme ve e-paper/OLED davranışı.
6. Öğrenci rehberinde yanlış parça satın alma veya yanlış bağlama doğurabilecek belirsizlikler.
7. İlk fiziksel doğrulama için en kısa test sırası.
```
