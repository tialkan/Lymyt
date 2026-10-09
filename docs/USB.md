# USB ile ilk çalıştırma

Wi-Fi ağı ve şifresi olmadan Nano ESP32'ye limit verisi göndermek için veri aktarabilen USB-C kablo kullanılır. Aynı kablo kartı besler. Bu sürüm yerel bilgisayar açıkken çalışır; VPS/domain gerekmez.

`firmware/Lymyt/config.h` içinde:

```cpp
#define LYMYT_USB_SERIAL true
#define LYMYT_RIGHT_EYE_ENABLED true
#define LYMYT_LED_PIN A0
#define LYMYT_USE_ADXL345 false
#define LYMYT_MOTION_PIN -1
#define LYMYT_BUTTON_PIN -1
```

Ekran ve LED kabloları [breadboard rehberindeki](BREADBOARD.md) gibi olmalıdır. LED seri 330 Ω dirençle A0'a bağlanır. Panel sınıfı `GxEPD2_154_D67` Waveshare siyah-beyaz V2/SSD1681 içindir; taşıyıcı rev2.1 yazısı panel kimliğini tek başına doğrulamaz.

Arduino IDE'de kart **Arduino Nano ESP32**, Pin Numbering **By Arduino pin**, USB Mode **Normal mode (TinyUSB)**. Kart paketi Arduino ESP32 Boards 2.0.18-arduino.5; GxEPD2 1.6.9, Adafruit GFX 1.12.6, Adafruit BusIO 1.17.4 ve ArduinoJson 7.4.3 ile USB sürümü derlendi. config.h Git'e alınmaz. USB modunda Wi-Fi ve HTTP anahtar alanları kullanılmaz.

Yükleme tamamlandıktan sonra IDE'nin **Serial Monitor/Plotter** panelini kapalı tut. Veri köprüsü seri portu kullanır; aynı portu başka programla açma. Terminalde:

```sh
cd /Users/baris/Documents/GitHub/Lymyt
python3 bridge/lymyt.py serve --serial-port /dev/cu.usbmodemE8F60AD38D242
```

USB kısa süre kopup aynı portla geri geldiğinde yardımcı 3 saniyede bir aynı seçili portu yeniden açmayı dener. Başka bir USB cihazına geçmez. Yeniden takıldığında port adı değişirse IDE'nin kart menüsünde Nano'nun güncel `/dev/cu.usbmodem…` portunu görüp komutu buna göre güncelle. `Address already in use` hatasında aynı yardımcı ikinci kez başlatılmıştır; önce çalışan yardımcının terminalinde Ctrl+C kullan.

Köprü gerçek Codex limitlerini okur; Claude Code için mevcut status line aktarımını kullanır. USB'ye yalnız normalize edilmiş limit bilgisi gönderilir; hesap anahtarı veya transkript gönderilmez. Ek Python kütüphanesi gerekmez (macOS/Linux).

Konsolda `Lymyt USB firmware ready.` kartın USB sürümünün çalıştığını; `USB quota frame acknowledged: …` kartın geçerli veri çerçevesini aldığını gösterir. Bu yanıt ekran camında görüntü oluştuğunun kanıtı değildir. `Busy Timeout!` mesajı panelin BUSY/CS/RST hattını veya sürücü kimliğini kontrol etmeyi gerektirir.

İlk açılışta firmware USB verisini en fazla 30 saniye bekler. Gözler 3 dakikalık tam yenileme aralığını korur; köprü her 15 saniyede bir veri gönderir. 45 saniye USB verisi alınmazsa bağlantı eski sayılır; sağlayıcı verisi 180 saniyeyi aşınca nötr/son bilinen duruma geçer. Eksik Claude bilgisi %0 kullanım olarak gösterilmez.

Yerel Lymyt Studio: <http://127.0.0.1:8787>. Bağlantı anahtarı yerel `.lymyt/device-token` dosyasındadır; yalnız kendi Studio alanına gir. USB aktarımı bu anahtarı gerektirmez. Yardımcı kapanınca yeni veri gönderimi durur.

Wi-Fi'a geçmek için köprüyü durdur, `LYMYT_USB_SERIAL false` yap ve [ASSEMBLY.md](ASSEMBLY.md) içindeki LAN/HTTPS ayarlarını kullanıp yeniden yükle.
