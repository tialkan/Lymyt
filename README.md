# Lymyt

İki e-paper gözüyle Codex ve Claude Code limitlerini taşıyan masa arkadaşı. Nano ESP32, iki siyah-beyaz Waveshare 1.54″ modül, mavi LED ve isteğe bağlı ADXL345/hareket sensörü.

- `web/`: Lymyt Studio; bağımsız göz ifadeleri, demo/gerçek veri ayrımı, kısa ve haftalık limitler, cihaz durumu.
- `bridge/lymyt.py`: Python 3.9+ bilgisayar yardımcısı ve VPS relay. Ek Python paketi gerektirmez.
- `firmware/Lymyt/`: iki SPI ekran, LED tepkileri, ADXL345 eğim/sallama ve hareket girişi için firmware prototipi.
- `docs/HARDWARE.md`: breadboard kablolaması.
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

Mevcut status line varsa önce yedekle/birleştir. Proje bu ayarı otomatik değiştirmez. Yalnızca limit alanları kaydedilir; hesap anahtarları veya transkriptler okunmaz. Pro/Max hesaplarında alanlar ilk API yanıtından sonra gelir. Eksik veriler sıfır sayılmaz. Gerçek Claude oturumundan veri alımı henüz doğrulanmadı.

## Donanım

[Kablolama rehberi](docs/HARDWARE.md). `config.example.h` dosyasını `config.h` olarak kopyala. Panel sürücüsü üretici sayfasına göre V2/SSD1681 varsayımıdır; **rev2.1** taşıyıcı kart yazısı tek başına kesin panel kimliği değildir. Üreticinin tek ekran örneğiyle doğrula.

İlk kurulum USB-C güç ve Wi-Fi veri kullanır. E-paper seyrek ifade değiştirir; LED hızlı etkileşim verir. Kısmi yenileme varsayılan kapalıdır. Firmware henüz derlenmedi, yüklenmedi veya gerçek donanımda test edilmedi.

## VPS

[tezatlas.info dağıtım rehberi](docs/DEPLOY.md). Yerel yardımcı HTTPS üzerinden yalnızca normalize edilmiş limit verilerini VPS'e yükler. Bilgisayar uyuduğunda VPS son gözlemi korur ve eski olduğunu işaretler; limitleri yeniden okuyamaz. Hesap tokenları VPS'e taşınmaz.

## Kontroller

```sh
python3 -m unittest discover -s tests -v
node --check web/app.js
```

12 test: eksik alanlar, %0 kullanımı, biten geri sayım, çoklu Codex kovası, eski veri, HTTP yetkilendirmesi, ayrı relay yazma anahtarı ve telemetri. Gerçek Codex bağlantısı ayrıca kontrol edildi. Sensör eşikleri ve ekran yenilemesi fiziksel doğrulama bekliyor.

## Kaynaklar

[Arduino](https://docs.arduino.cc/hardware/nano-esp32), [Waveshare](https://www.waveshare.com/wiki/1.54inch_e-Paper_Module_Manual), [Codex app-server](https://learn.chatgpt.com/docs/app-server), [Claude status line](https://code.claude.com/docs/en/statusline), [GxEPD2](https://github.com/ZinggJM/GxEPD2), [ADXL345](https://github.com/adafruit/Adafruit_ADXL345).
