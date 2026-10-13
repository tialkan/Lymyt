# Lymyt

İki e-paper gözüyle Codex ve Claude Code limitlerini taşıyan masa arkadaşı. Nano ESP32, iki siyah-beyaz Waveshare 1.54″ modül, mavi LED ve isteğe bağlı ADXL345/hareket sensörü.

- `web/`: Lymyt Studio; bağımsız göz ifadeleri, demo/gerçek veri ayrımı, kısa ve haftalık limitler, cihaz durumu.
- `bridge/lymyt.py`: Python 3.9+ bilgisayar yardımcısı ve VPS relay. Ek Python paketi gerektirmez.
- `firmware/Lymyt/`: iki e-paper SPI veya iki SSD1306 I2C ekran, C1 kelime modu, LED tepkileri, ADXL345 eğim/sallama ve hareket girişi için firmware prototipi.
- `docs/ASSEMBLY.md`: gerçek devre için adım adım kurulum ve sorun giderme.
- `docs/BREADBOARD.md`: tek göz, iki göz ve sensör için numaralı deliklerle üç bağlantı çizimi.
- `docs/USB.md`: Wi-Fi şifresi olmadan USB üzerinden ilk çalıştırma.
- `docs/HARDWARE.md`: pin planı ve doğrulanan kütüphaneler.
- `Dockerfile`, `compose.yaml`: VPS/Coolify dağıtımı. Hesap oturumları bilgisayarda kalır.

## Bilgisayarda çalıştır

```sh
python3 bridge/lymyt.py serve
```

`http://127.0.0.1:8787` adresini aç. Arayüz örnek verilerle başlar. Gerçek veriye bağlanmak için `.lymyt/device-token` dosyasındaki anahtarı gir. Anahtar yalnızca sayfa belleğinde tutulur.

Codex CLI kurulu ve ChatGPT hesabıyla giriş yapılmış olmalıdır. Yardımcı sadece `account/rateLimits/read` çağırır; model isteği veya limit sıfırlama yapmaz. Bu bilgisayarda gerçek Codex bağlantısı ve iki limit penceresi doğrulandı. Yalnızca UI için `serve --no-codex`, yerel Wi-Fi'daki Nano için `serve --host 0.0.0.0` kullan.

## Claude Code

Status line JSON'unu okuyan komut:

```sh
python3 /Users/baris/Documents/GitHub/Lymyt/bridge/lymyt.py capture-claude
```

Kullanıcı ayarlarına eklenebilecek örnek:

```json
{
  "statusLine": {
    "type": "command",
    "command": "python3 /Users/baris/Documents/GitHub/Lymyt/bridge/lymyt.py capture-claude",
    "refreshInterval": 60
  }
}
```

Mevcut status line varsa önce yedekle/birleştir. Yardımcı bu ayarı otomatik değiştirmez. Bu Mac'te kurulum sırasında status line ayarı eklendi; önceki durum `.lymyt/claude-statusline-before.json` içinde yedeklendi. Yalnızca limit alanları kaydedilir; hesap anahtarları veya transkriptler okunmaz. Pro/Max hesaplarında alanlar ilk API yanıtından sonra gelir. Eksik veriler sıfır sayılmaz. 9 Ekim 2026: Claude Code oturumu Team hesabıyla açıldı. Otomatik statusline kota alımı henüz doğrulanmadı; tarayıcıdan alınan son kullanım örneği claude-browser-manual kaynağıyla işaretlenir. Tekrarlanan önbellek payloadı gözlem zamanını yenilemez.

## Donanım

[Numaralı breadboard çizimleri](docs/BREADBOARD.md), [adım adım devre rehberi](docs/ASSEMBLY.md) ve [pin planı](docs/HARDWARE.md). `config.example.h` dosyasını `config.h` olarak kopyala. Panel sürücüsü üretici sayfasına göre V2/SSD1681 varsayımıdır; **rev2.1** taşıyıcı kart yazısı tek başına kesin panel kimliği değildir. Üreticinin tek ekran örneğiyle doğrula.

USB girişli ve pinleri lehimli klasik ESP32-WROOM kartı için [lehimsiz WROOM kurulum rehberi](docs/WROOM-ASSEMBLY.md) kullanılır. Nano'nun delik koordinatları bu karta taşınmaz. `BoardPins.h` kart seçimine göre pinleri belirler; WROOM'da `config.wroom.example.h` → `config.h`. `PanelCheckWroom` testi ana yazılımdan önce uygulanır. Harici LED kaldırıldı; iki e-ink ortak hatları breadboard üzerinde dağıtılır. 12 Ekim 2026'da Espressif core 2.0.17 / ESP32 Dev Module ile WROOM test ve ana sketch'leri ve Arduino Nano ESP32 ile ana firmware derlendi. WROOM'a yükleme ve fiziksel ekran testi henüz yapılmadı.

İlk kurulumda [USB üzerinden veri aktarımı](docs/USB.md) veya Wi-Fi kullanılabilir; kart USB-C ile beslenir. E-paper seyrek ifade değiştirir; LED hızlı etkileşim verir. Kısmi yenileme varsayılan kapalıdır. 9 Ekim 2026'da iki ekran ve A0 LED seçenekli USB sürümü Arduino IDE'den gerçek Nano ESP32'ye başarıyla yüklendi. Nano gerçek Codex limit çerçevelerini USB üzerinden aldığını doğruladı. Son fiziksel kontrol: Nano headerları henüz lehimlenmemiş, iki ekran beyaz. Kartın onboard mavi LED’i PanelCheck ile yanıp sönüyor; bu ekran bağlantısının doğrulandığı anlamına gelmez. Şu an cihazda PanelCheck bulunuyor. Yeni kelime/OLED firmware’i derlendi, cihaza yüklenmedi. ADXL345 bağlı olmadığı için kapalı.

## VPS

[tezatlas.info dağıtım rehberi](docs/DEPLOY.md). Yerel yardımcı HTTPS üzerinden yalnızca normalize edilmiş limit verilerini VPS'e yükler. Bilgisayar uyuduğunda VPS son gözlemi korur ve eski olduğunu işaretler; limitleri yeniden okuyamaz. Hesap tokenları VPS'e taşınmaz.

## Kontroller

```sh
python3 -m unittest discover -s tests -v
node --check web/app.js
```

19 köprü/USB testi: eksik alanlar, %0 kullanımı, biten geri sayım, çoklu Codex kovası, eski veri, HTTP yetkilendirmesi, ayrı relay yazma anahtarı ve telemetri. Gerçek Codex bağlantısı ayrıca kontrol edildi. Firmware derlemesi: Arduino ESP32 Boards 2.0.18-arduino.5, GxEPD2 1.6.9, ArduinoJson 7.4.3, Adafruit GFX 1.12.6, ADXL345 1.3.4, Unified Sensor 1.1.15. Sensörlü sürüm flash alanının %32'sini, statik RAM'in %20'sini kullanıyor. Sensör eşikleri ve ekran yenilemesi fiziksel doğrulama bekliyor.

## Kaynaklar

[Arduino](https://docs.arduino.cc/hardware/nano-esp32), [Waveshare](https://www.waveshare.com/wiki/1.54inch_e-Paper_Module_Manual), [Codex app-server](https://learn.chatgpt.com/docs/app-server), [Claude status line](https://code.claude.com/docs/en/statusline), [GxEPD2](https://github.com/ZinggJM/GxEPD2), [ADXL345](https://github.com/adafruit/Adafruit_ADXL345).

## Sıfırdan tasarım / TezAtlas

Asıl web sayfası `/Users/baris/Documents/GitHub/tezatatlascom/src/app/lymyt` içinde, mevcut PortalShell ve tema ile geliştirilir. Yayın hedefi https://tezatlas.com/lymyt. Robotistan örnek alışveriş listesi, breadboard/plaket adımları, OLED alternatifi, indirilebilir sanitizeli kaynak paketi, STL/SCAD ve ikinci görüş promptu içerir. Public önizleme kişisel hesap verilerini göstermez.

- `data/words.json`: 24 C1 kart; `python3 tools/generate_words.py` firmware destesini üretir.
- `firmware/Lymyt/Learning.h`: limit/kelime döngüsü, bekleyen yenilemede kelime atlamayı önleme. İlerleme Nano NVS’de kalır.
- `enclosure/`: 150×100×55mm ölçü deneme gövdesi, ayrı kapak ve 60×44mm uyum test STL’si; parametrik SCAD. `python3 enclosure/generate.py` manifold kenarları doğrulayarak STL üretir. Gerçek parça ölçüleri ve fiziksel baskı doğrulanmalı.
- `docs/PUBLIC-GUIDE.md`: indirilebilir paket başlangıç rehberi.
- `docs/SECOND-OPINION.md`: başka LLM’den bağımsız tasarım incelemesi almak için prompt.
- OLED: iki4pin128×64SSD1306, adres0x3C, solA4/A5 sağA2/A3. SH1106/SPI aynı sürücü kabul edilmez.

9 Ekim kontrolleri: TypeScript ve üretim Next.js build başarılı; e-paper ve OLED ayrı ayrı derlendi; kelime destesindeki bütün Türkçe karakterler fontta mevcut. 19Python testi ve host üzerinde C++ öğrenme döngüsü testi geçti. STL’lerde her kenar iki yüz paylaşır. Bunlar fiziksel devre/baskı doğrulaması değildir.

```sh
c++ -std=c++11 tests/test_learning.cpp -o /tmp/lymyt-learning-test
/tmp/lymyt-learning-test
```
