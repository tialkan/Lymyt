"use client";
import { useState } from "react";
import s from "./lymyt.module.css";

const connections = [
  ["3V3", "a1", "c1 → VCC", "d1 → VCC"],
  ["GND", "a2", "c2 → GND", "d2 → GND"],
  ["D23 / GPIO23", "a3", "c3 → DIN", "d3 → DIN"],
  ["D18 / GPIO18", "a4", "c4 → CLK", "d4 → CLK"],
  ["D27 / GPIO27", "a5", "c5 → CS", "—"],
  ["D26 / GPIO26", "a6", "c6 → DC", "—"],
  ["D25 / GPIO25", "a7", "c7 → RST", "—"],
  ["D34 / GPIO34", "a8", "c8 → BUSY", "—"],
  ["D33 / GPIO33", "a9", "—", "d9 → CS"],
  ["D32 / GPIO32", "a10", "—", "d10 → DC"],
  ["D14 / GPIO14", "a11", "—", "d11 → RST"],
  ["D35 / GPIO35", "a12", "—", "d12 → BUSY"],
];
export default function WroomGuide({ screen }: { screen: string }) {
  const [step, setStep] = useState(3);
  const [button, setButton] = useState(false);
  const oled = screen === "oled";
  const file = oled ? "wroom-oled" : button ? "wroom-breadboard-4" : `wroom-breadboard-${step}`;
  return <>
    <p className={s.callout}><b>ESP32-WROOM: kart breadboard dışında, iki ekran birlikte.</b> Pinleri lehimli 30 pinli klasik WROOM geliştirme kartını yalıtkan yüzeyde tut. Dişi jumper uçları kartın alt pinlerine, erkek uçları breadboard’a girer. Harici LED gerekmez. Çizimin GPIO planı firmware ile eşleşir; görünür ekran testi gerçek devrede yapılır.</p>
    {!oled && <><div className={s.steps} aria-label="WROOM devre adımları">{["Ortak besleme", "Sol göz", "İki göz · tam şema"].map((label, i) => <button key={label} aria-pressed={step === i + 1 && !button} onClick={() => { setStep(i + 1); setButton(false); }}><b>0{i + 1}</b>{label}</button>)}</div><div className={s.options}><label><input type="checkbox" checked={button} onChange={e => setButton(e.target.checked)} /> İsteğe bağlı kelime düğmesini de göster</label></div></>}
    <figure className={s.diagram}><a href={`/lymyt-assets/${file}.svg`} target="_blank" rel="noopener"><img src={`/lymyt-assets/${file}.svg`} alt={oled ? "ESP32-WROOM iki SSD1306 OLED bağlantısı" : "ESP32-WROOM breadboard üzerinde iki e-ink, LED’siz bağlantı"} loading="lazy" /></a><figcaption>Çizimi büyütmek için dokun. Kart pin sırası örnek 30 pinli WROOM’a aittir; ekran ve buton terminal sırası temsilîdir. Kablo rengine göre değil, parçanın üzerindeki pin adına göre bağla.</figcaption></figure>
    {oled ? <div className={s.guideCopy}><ol><li>Sol OLED: VCC=3V3, GND=GND, SDA=GPIO21, SCL=GPIO22. Sağ OLED: VCC=3V3, GND=GND, SDA=GPIO16, SCL=GPIO17.</li><li>İki 128×64 SSD1306 I²C ekran ayrı donanım hatlarında aynı 0x3C adresini kullanır. SH1106 veya SPI ekran için bu çizim kullanılmaz.</li><li><code>LYMYT_OLED true</code>; LED kapalı. WROOM config dosyasında sensörler ilk aşamada kapalı kalır.</li></ol></div> : <>
      <div className={s.compare}><article><h3>Bir pine iki kablo sıkıştırma.</h3><p>Örnek: ESP32 GPIO23 → <b>a3</b>. Sol DIN → <b>c3</b>; sağ DIN → <b>d3</b>. Aynı sırada a–e içeriden bağlı olduğu için tek GPIO kablosu iki ekrana dağıtılır. Aynı yöntem 3V3, GND ve CLK için de kullanılır.</p><b>Her kart pininde yalnız bir dişi jumper.</b></article><article><h3>Kontrol hatları ayrı.</h3><p>CS, DC, RST ve BUSY iki ekran arasında paylaşılmaz. İlk 12 sıra bütün ekran hatlarına yeter; küçük 17 sıralı breadboard’da da kurulur. Ortadaki yarığın f–j tarafı bu devrede kullanılmaz.</p><b>Kesişen kablolar bağlantı oluşturmaz.</b></article></div>
      <div className={s.tableWrap}><table className={s.pinTable}><caption>İki e-ink · tam kablo listesi · ESP32 GPIO → a deliği; sol ekran c, sağ ekran d</caption><thead><tr><th>ESP32 pini</th><th>Karttan gelen kablo</th><th>Sol ekran kablosu</th><th>Sağ ekran kablosu</th></tr></thead><tbody>{connections.map(row => <tr key={row[0]}>{row.map((v, i) => <td key={i}>{v}</td>)}</tr>)}</tbody></table></div>
      <div className={s.guideCopy}><ol><li><b>USB çıkarılmışken kur.</b> Kart → breadboard 12 kablo; ekran → breadboard 8+8 kablo. Toplam 28 bağlantı; ekranın kutusundan çıkan kablolar buna dahildir. VIN boş kalır; ekran VCC’si 3V3’e gider.</li><li><b>Önce görünür görüntüyü doğrula.</b> Arduino IDE’de ESP32 Dev Module seç; PanelCheckWroom yükle. Seri Monitör 115200: <code>s</code> pinleri, <code>l</code> sol, <code>r</code> sağ ekranı test eder. Diğer ekran CS ile seçilmemiş tutulur.</li><li><b>Sonra ana yazılım.</b> config.wroom.example.h → config.h; USB=true, OLED=false, RIGHT_EYE_ENABLED=true, LED_PIN=-1, BUTTON_PIN=-1. İki ekran görüntü verdiğinde Lymyt.ino yükle. Seri Monitör’ü kapatıp yardımcıyı gerçek USB portuyla başlat.</li><li><b>Kelime düğmesi sonra.</b> GPIO4 → a14; butonun basınca birleşen iki ayrı grubu b14 ve b2’ye. <code>LYMYT_BUTTON_PIN 4</code>. LED gerekmez; e-paper geçişi yenileme zamanını bekler.</li></ol></div>
      <p className={s.callout}>Rev2.1 yazısı taşıyıcı kartın revizyonudur; ekran denetleyicisini kesinleştirmez. GxEPD2_154_D67 sürücüsü henüz gerçek ekranda doğrulanmadı. Derleme ve kablo planı kontrolü geçti; iki ekranın bu kartta görüntü testi bekliyor.</p>
      <div className={s.actions}><a href="/lymyt-assets/wroom-epaper-full.svg" download>İki e-ink tam şema SVG ↓</a><a href="/lymyt-assets/wroom-epaper-full.png" download>İki e-ink tam şema PNG ↓</a></div>
    </>}
  </>;
}
