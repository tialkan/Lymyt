# Lymyt · Sıfırdan tasarım

Görsel rehber: https://tezatlas.com/lymyt

## İlk kurulum

1. Nano ESP32 headerlarını lehimle. Güç kapalıyken tek ekranı bağla. Panel modeli ve sürücüsünü PanelCheck ile doğrula; carrier Rev2.1 yeterli kimlik değildir.
2. Kart seçimi: Nano ESP32 için Arduino Nano ESP32 / By Arduino pin; klasik WROOM için esp32 by Espressif Systems / ESP32 Dev Module. WROOM bağlantıları docs/WROOM-ASSEMBLY.md içindedir. ArduinoJson, Adafruit GFX ve U8g2_for_Adafruit_GFX kur. E-paper için GxEPD2; OLED için Adafruit SSD1306.
3. Nano için config.example.h, WROOM için config.wroom.example.h dosyasını aynı klasöre config.h olarak kopyala. USB varsayılan. E-paper: LYMYT_OLED false. 128×64 SSD1306 I2C: true. Buton bağlandıysa LYMYT_BUTTON_PIN D2; WROOM düğmesi için GPIO4. Harici LED kullanılmaz, LED_PIN=-1. Bağlı olmayan sensörleri açma.
4. E-paper ortak DIN=D11, CLK=D13, VCC=3V3 ve GND; sol CS/DC/RST/BUSY D10/D9/D8/D7, sağ D6/D5/D4/D3. OLED sol SDA=A4/SCL=A5, sağ SDA=A2/SCL=A3; ikisi0x3C, ayrı I2C hatları.
5. Arduino IDE'den kodu yükle. Seri monitörü kapat. macOS/Linux'ta port adını IDE'den al:
   python3 bridge/lymyt.py serve --serial-port /dev/cu.usbmodemGERCEK_PORT
   Windows USB aktarımı bu yardımcıda desteklenmiyor.
6. Codex CLI oturumu açık olmalı. Claude Code için claude auth login ve resmî statusline command: python3 /tam/yol/bridge/lymyt.py capture-claude. Plan/oturum kısıtları: https://code.claude.com/docs/en/statusline
7. Studio http://127.0.0.1:8787; gerçek kota ekranı için yardımcı ilk açılışta .lymyt/device-token üretir. Bu dosyayı paylaşma. Public sayfa örnek veri kullanır.

## Düğme

D2 → anlık buton → GND, INPUT_PULLUP. Limit → kelime → öğrendim ve limit → sonraki kelime. İlerleme Nano NVS belleğinde kalır. E-paper tam yenileme varsayılan180sn, gerçek panelde doğrulanmış kısmi mod60sn; bekleyen geçişte ek basışlar atılır. OLED hızlı geçiş yapar. E-paper'da kelime öğrenme temposu yavaştır; sık çalışma için OLED seçeneğini kullan.

## Gövde

enclosure/lymyt.scad parametrelerini ölçüye göre düzenle. Body150×100×55mm, kapak2.4mm. Önce fit-test60×44mm dosyasını yazdır. Büyük830delikli breadboard dahil değil; kalıcı devre50×100mm yalıtılmış pedli delikli pertinaks. Ekran/kart/USB/pil yuvası gerçek ölçüleri ve iç sabitleme prototipte doğrulanmalı. Ekran camını/flex kabloyu sıkıştırma. Kablo alanı≥8mm.

Baskı başlangıcı:0.4mm nozül,0.2mm katman,3duvar,%15–20dolgu; slicer köprülerini kontrol et. STL mm. Gövde yüzü tablada; kapak düz.4M3×16vida ve4somun. Ölçü deneme tasarımı; fiziksel baskı/test tamamlanmış kabul edilmez.

## Pil

Önce USB.4eş NiMHAA→anahtar→düşük gerilim korumalı5Vbuck-boost→NanoUSB-C. Yaklaşık4–6Vgirişte5V/≥1Asürekli veWiFi piklerini doğrula. Model kesinleşmeden rastgeleboostkartısatınalma. Pilleri VIN'e doğrudan bağlama. Nano şarj etmez; haricîNiMHşarjcihazı. Regülatör ve bilgisayar USB beslemesini paralelleme. Pil süresi henüz ölçülmedi.

## Kaynak ve lisans notları

24 C1 kelime: düzeyleri Oxford5000CEFR listesinden kontrol edilen bir seçim; Türkçe anlamlar ve örnekler bu proje için yazıldı. Oxford word list: https://www.oxfordlearnersdictionaries.com/external/pdf/wordlists/oxford-3000-5000/The_Oxford_5000_by_CEFR_level.pdf

Üçüncü taraf Arduino kütüphaneleri pakete gömülü değildir; kendi lisanslarıyla Arduino Library Manager üzerinden kurulur. Unicode fontu U8g2_for_Adafruit_GFX sağlar; Unifont lisansı font embedding exception içerir. Paket hesap tokenı, Wi-Fi parolası, kişisel quota veya config.h içermez.
