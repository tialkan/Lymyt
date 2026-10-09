# Lymyt

İki e-paper gözüyle Codex ve Claude Code limitlerini taşıyan masa arkadaşı. Nano ESP32, iki siyah-beyaz Waveshare 1.54″ modül, mavi LED ve isteğe bağlı ADXL345/hareket sensörü.

- `web/`: Lymyt Studio; bağımsız göz ifadeleri, demo/gerçek veri ayrımı, kısa ve haftalık limitler, cihaz durumu.
- `bridge/lymyt.py`: Python 3.9+ bilgisayar yardımcısı ve VPS relay. Ek Python paketi gerektirmez.
- `firmware/Lymyt/`: iki SPI ekran, LED tepkileri, ADXL345 eğim/sallama ve hareket girişi için firmware prototipi.
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

Mevcut status line varsa önce yedekle/birleştir. Yardımcı bu ayarı otomatik değiştirmez. Bu Mac'te kurulum sırasında status line ayarı eklendi; önceki durum `.lymyt/claude-statusline-before.json` içinde yedeklendi. Yalnızca limit alanları kaydedilir; hesap anahtarları veya transkriptler okunmaz. Pro/Max hesaplarında alanlar ilk API yanıtından sonra gelir. Eksik veriler sıfır sayılmaz. Gerçek Claude oturumundan veri alımı henüz doğrulanmadı.

## Donanım

[Numaralı breadboard çizimleri](docs/BREADBOARD.md), [adım adım devre rehberi](docs/ASSEMBLY.md) ve [pin planı](docs/HARDWARE.md). `config.example.h` dosyasını `config.h` olarak kopyala. Panel sürücüsü üretici sayfasına göre V2/SSD1681 varsayımıdır; **rev2.1** taşıyıcı kart yazısı tek başına kesin panel kimliği değildir. Üreticinin tek ekran örneğiyle doğrula.

İlk kurulumda [USB üzerinden veri aktarımı](docs/USB.md) veya Wi-Fi kullanılabilir; kart USB-C ile beslenir. E-paper seyrek ifade değiştirir; LED hızlı etkileşim verir. Kısmi yenileme varsayılan kapalıdır. 9 Ekim 2026'da iki ekran ve A0 LED seçenekli USB sürümü Arduino IDE'den gerçek Nano ESP32'ye başarıyla yüklendi. Nano gerçek Codex limit çerçevelerini USB üzerinden aldığını doğruladı. Panel görüntüsü ve LED'in fiziksel çalışması kullanıcıdan doğrulama bekliyor; ADXL345 bağlı olmadığı için kapalı. USB ve Wi-Fi sürümleri derlendi, 18 köprü/USB testi geçti. Gerçek Claude verisi henüz gelmedi.

## VPS

[tezatlas.info dağıtım rehberi](docs/DEPLOY.md). Yerel yardımcı HTTPS üzerinden yalnızca normalize edilmiş limit verilerini VPS'e yükler. Bilgisayar uyuduğunda VPS son gözlemi korur ve eski olduğunu işaretler; limitleri yeniden okuyamaz. Hesap tokenları VPS'e taşınmaz.

## Kontroller

```sh
python3 -m unittest discover -s tests -v
node --check web/app.js
```

12 test: eksik alanlar, %0 kullanımı, biten geri sayım, çoklu Codex kovası, eski veri, HTTP yetkilendirmesi, ayrı relay yazma anahtarı ve telemetri. Gerçek Codex bağlantısı ayrıca kontrol edildi. Firmware derlemesi: Arduino ESP32 Boards 2.0.18-arduino.5, GxEPD2 1.6.9, ArduinoJson 7.4.3, Adafruit GFX 1.12.6, ADXL345 1.3.4, Unified Sensor 1.1.15. Sensörlü sürüm flash alanının %32'sini, statik RAM'in %20'sini kullanıyor. Sensör eşikleri ve ekran yenilemesi fiziksel doğrulama bekliyor.

## Kaynaklar

[Arduino](https://docs.arduino.cc/hardware/nano-esp32), [Waveshare](https://www.waveshare.com/wiki/1.54inch_e-Paper_Module_Manual), [Codex app-server](https://learn.chatgpt.com/docs/app-server), [Claude status line](https://code.claude.com/docs/en/statusline), [GxEPD2](https://github.com/ZinggJM/GxEPD2), [ADXL345](https://github.com/adafruit/Adafruit_ADXL345).
