# Beyaz ekran tanılaması

9 Ekim 2026: kullanıcı iki ekranın da beyaz kaldığını bildirdi. USB kota ACK'leri görüntü oluştuğunu doğrulamaz. `firmware/PanelCheck/PanelCheck.ino` gerçek Nano ESP32'ye DFU üzerinden yüklendi; yükleme hatasız tamamlandı. Bu test sırasında normal Lymyt köprüsü durduruldu. Kartta şu anda **PanelCheck** vardır, kota firmware'i değildir.

Test Wi-Fi veya kota verisi kullanmaz. Arduino pin adlarını kullanır; SCK=D13, MOSI=D11 açıkça seçilmiştir. SPI 1 MHz, reset darbesi 5 ms'dir; 5 ms, [Waveshare V2 örneğinde](https://github.com/waveshareteam/e-Paper/blob/master/Arduino/epd1in54_V2/epd1in54_V2.cpp) kullanılan süredir. Sürücü hâlâ geçici `GxEPD2_154_D67` / SSD1681 seçimidir. **Rev2.1 taşıyıcı kart yazısı panel denetleyicisini belirlemez.**

Her ekran ayrı CS ile tek seferlik test deseni alır: siyah üst şerit, LYMYT yazısı, LEFT/RIGHT, iki siyah daire. GxEPD2 ilk kullanımda ayrıca başlangıç temizliği yapar. Sürekli yenileme yoktur; aynı ekrana tekrar komut için 3 dakika beklenir. BUSY sadece giriş olarak okunur. Yenilemeden sonra BUSY kopuk olabileceği için besleme kapatma komutundan önce ayrıca 5 saniye beklenir. A0 üzerindeki mevcut dirençli LED iki saniyede bir 150 ms yanar. İkinci tanılama sürümünde Nano'nun dahili RGB LED'i de aynı ritimde mavi yanar; böylece header teması olmadan kartın çalıştığı optik olarak kontrol edilebilir. D13 ışığı SPI ile ortak olduğundan heartbeat için kullanılmaz. Kart üzerindeki ayrı yeşil güç LED'i sabit yanabilir.

## Gerçek ölçüm

| Test | Yenileme çağrıları boyunca süre | BUSY değişimleri |
|---|---:|---|
| Sol | 407 ms | 0; son seviye LOW |
| Sağ | 410 ms | 107270; son seviye LOW |

Kütüphanenin `_Update_Full` beklemeleri her iki panelde 2–3 **mikrosaniye** sürdü. Bunlar normal bir e-paper yenilemesinin optik doğrulaması değildir. Sağ hattaki çok hızlı geçişler gürültü/kararsız giriş olasılığını, sol hattaki sabit LOW ise yanıt alınmadığını düşündürür. Eksik güç, ortak GND, yanlış/kopuk kablo, header teması veya yanlış panel sürücüsü henüz ayrıştırılmadı. Ekranların bozuk olduğu sonucuna varılamaz.

Nano'dan okunan GPIO eşlemesi: D13=48, D11=38; sol CS/DC/RST/BUSY=21/18/17/10; sağ=9/8/7/6. Arduino pin numarası ayarı ve yazılım eşlemesi beklenen değerlerdedir. Bu, kablonun modül ucuna ulaştığının ölçümü değildir.

Yerel ham kayıtlar `.lymyt/panelcheck-left.log` ve `.lymyt/panelcheck-right.log` içinde tutulur; Git'e alınmaz.

## Fiziksel kontrol sırası

Kablo değiştirirken USB'yi çıkar. Önce ortak beslemeyi kontrol et: Nano **3V3** çıkışı iki modülün **VCC** pinine, Nano **GND** iki modülün **GND** pinine ulaşmalı. [Breadboard çiziminde](BREADBOARD.md) bunun için a6→a22 ve b18→a23 jumper'ları gerekir. 22/23 numaralı sıraların a–e ve f–j tarafları orta boşluk üzerinden birbirine bağlı değildir. Header'lar lehimli olmalı; boş deliklere gevşekçe geçirilen pinler güvenilir temas sağlamaz.

| Ekran üzerinde yazan pin | Sol ekran → Nano | Sağ ekran → Nano |
|---|---|---|
| VCC | 3V3 | 3V3 |
| GND | GND | GND |
| DIN | D11 | D11 |
| CLK | D13 | D13 |
| CS | D10 | D6 |
| DC | D9 | D5 |
| RST | D8 | D4 |
| BUSY | D7 | D3 |

Kablo rengini veya çizimdeki modül terminal sırasını değil, gerçek kart üzerindeki pin adını izle. Nano'nun D11 etiketi GPIO11 değildir. Kartta 3-wire/4-wire anahtarı varsa mevcut konumu ve baskısı kontrol edilmeli; bu yazılım ayrı DC hattıyla 4-wire SPI kullanır. Ek PWR pini olan kart için kartın tam modelini doğrulamadan rastgele bağlantı yapılmaz. Multimetre varsa, USB bağlıyken ekranın kendi VCC ve GND uçları arasında yaklaşık 3.3 V ölçülmeli.

Panelin arkasındaki model/V2 etiketi ve breadboard'u gösteren net bir fotoğraf, sürücü ve gerçek kablo sırasını doğrulamak için gereken sonraki bilgidir.

## Fotoğrafta şüphe edilen header teması

Kullanıcının IMG_3163.heic fotoğrafındaki şüphe doğrulandı: **kullanıcı Nano pinlerini lehimlemediğini ve dahili mavi ışığın yanıp söndüğünü bildirdi.** Böylece test yazılımının çalışması gözle doğrulandı; breadboard'a giden header teması ise henüz kurulmamış. Harici LED yanmıyor ve ekranlar beyaz. Fotoğraftaki kablolar bazı pinleri kapattığından tüm bağlantılar kesin olarak izlenemedi.

Lehimsiz header'ın üstüne kartı oturtmak, breadboard ile Nano arasında güvenilir bağlantı sağlamaz. USB'nin çalışması ve yeşil güç ışığı yanması dış pinlerin bağlı olduğunu kanıtlamaz. Sonraki gerekli adım iki header'ın Nano'ya lehimlenmesidir; yazılım değişikliği bu fiziksel teması düzeltmez. Panel sürücüsü ve kalan kablo planı ancak bu bağlantı düzeltildikten sonra doğrulanabilir.

Lehimsiz kart için iki adet **1×15, 2.54 mm erkek header** gerekir. Uzun pinler breadboard'a doğru aşağı, kısa uçlar Nano'nun deliklerinden yukarı gelecek; siyah plastik çıtalar kartın altında kalacak şekilde yerleştirilir. USB ve ekran kabloları çıkarılır. İki çıta hizalanıp sabitlendikten sonra kısa pinler ile kartın metal pad'leri birleştirilerek toplam 30 ayrı lehim bağlantısı yapılır; yan yana pad'ler lehimle köprülenmez. Breadboard deliklerine havya değdirilmez. İlk kez lehim yapılıyorsa kartı bir elektronikçiye götürüp iki header'ı lehimletmek uygulanabilir bir seçenektir.

Lehimden sonra önce Nano ve tek dirençli LED bağlanır. Dahili mavi ışıkla birlikte harici A0 LED'i de yanıp sönüyorsa, aynı [breadboard rehberinin](BREADBOARD.md) birinci aşamasıyla yalnız sol ekran eklenir ve `l` testi çalıştırılır. Kartın fotoğrafta USB'si aşağıda görünmesi kendi başına hata değildir; koordinatlar için Nano/breadboard yönü çizimdeki USB-yukarı görünüşle eşleştirilmelidir. Kablo renkleri ve örtülü yollar üzerinden pin ataması tahmin edilmez.

## Testi yeniden çalıştırma

Kablo düzeltildikten sonra USB takılır. Normal kota köprüsü kapalı kalmalı. IDE Serial Monitor'de 115200 baud ile `s` gönder: BUSY seviyeleri/pin eşlemesi. Ardından `l` sol test, `r` sağ test. Görünür resim ve birkaç saniyelik normal BUSY davranışı birlikte kontrol edilir. `RESULT` mesajı tek başına başarı demek değildir.

```sh
arduino-cli compile -b arduino:esp32:nano_nora:PinNumbers=default firmware/PanelCheck
arduino-cli upload -b arduino:esp32:nano_nora:PinNumbers=default -p /dev/cu.usbmodemE8F60AD38D242 firmware/PanelCheck
```

Nano ESP32, By Arduino pin, Normal/TinyUSB kullanılır. İlk derleme: 393297 byte flash, 41816 byte RAM; dahili RGB heartbeat eklenen sürüm: 393401 byte flash, 41816 byte RAM. GxEPD2 1.6.9 / Arduino ESP32 Boards 2.0.18-arduino.5 kullanıldı. İkinci sürüm de gerçek Nano'ya hatasız yüklendi; kullanıcı dahili mavi ışığın yanıp söndüğünü doğruladı.

Görüntü doğrulandıktan sonra Serial Monitor kapatılır, `firmware/Lymyt` USB yapılandırması tekrar yüklenir ve [USB köprüsü](USB.md) yeniden başlatılır. Test yazılımı kota ACK'leri göndermez.
