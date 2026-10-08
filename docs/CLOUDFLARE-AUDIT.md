# Cloudflare güvenlik çalışması: başlangıç ölçümü

8 Ekim 2026. Kullanıcı tüm Cloudflare sitelerinde güvenliği artırmayı istedi. Helium başka bir işlemde kullanıldığı için kullanıcı önce breadboard çizimlerinin tamamlanmasını seçti. **Bu aşamada Cloudflare güvenlik ayarlarında değişiklik yapılmadı.** Dashboard bulgularının site bazında incelenmesi ve uygulanabilir düzeltmelerin yapılması bekliyor.

Bu tablo önceki Cloudflare domain envanterindeki 12 alan adı ve eklenen tezatlas.info için dışarıdan yapılan HTTP/HTTPS HEAD kontrolüdür. Sertifika doğrulaması açık tutuldu; hesap yapılandırmasını veya origin sertifikasını doğrulamaz. Yanıtların WAF/istemci türüne göre değişebilmesi nedeniyle hata kodu tek başına tüm ziyaretçilerin aynı hatayı gördüğünü kanıtlamaz.

| Alan adı | HTTPS HEAD | HTTP isteğinin son adresi | HTTPS yanıtında HSTS |
|---|---|---|---|
| arslandedem.com | 200 | HTTPS | Görülmedi |
| baristiran.com | 503 | HTTP | Görülmedi |
| baristiran.info | 200 | HTTPS | Görülmedi |
| baristiran.online | 200 | HTTPS | Görülmedi |
| bitcoindogmode.com | 200 | HTTPS | 2 yıl, alt alanlar dahil |
| catsvstradfi.com | 200 | HTTP | 2 yıl, alt alanlar dahil |
| graphicltd.com | 200 | HTTPS | 2 yıl, alt alanlar dahil, preload başlığı |
| kazuist.com | 200 | HTTPS | 2 yıl, alt alanlar dahil, preload başlığı |
| kulular.com.tr | 200 | HTTPS | 2 yıl, alt alanlar dahil, preload başlığı |
| modelbes.com | 200 | HTTPS | 1 yıl, alt alanlar dahil |
| sigaramolasi.com | 200 | HTTPS | Görülmedi |
| tezatlas.com | 200 | HTTPS | Görülmedi |
| tezatlas.info | Bağlantı reddedildi | HTTP | Ölçülemedi |

İlk inceleme noktaları: baristiran.com'un 503 yanıtı, catsvstradfi.com'un HTTP yönlendirmesi, HTTPS'i çalışan sitelerde eksik HSTS, her sitede minimum TLS ve WAF durumları. HSTS alt alanları ve preload seçenekleri tüm alt alanlar doğrulanmadan genişletilmez. Mevcut daha güçlü ayarlar korunur. Full (strict) için origin sertifikası ayrıca doğrulanmalı; ziyaretçinin geçerli HTTPS sertifikası bunu tek başına kanıtlamaz. E-posta DNS kayıtları veya API/webhook uçları trafik türü incelenmeden topluca proxylanmaz/challenge'a alınmaz.

tezatlas.info için Cloudflare A kaydı/proxy ve VPS uygulaması hazırlanmıştı; nameserver devri için istenen işlem anı onayı henüz gelmedi. Bu tablo domainin Cloudflare üzerinden aktif yayınlandığını göstermez.

Ham ölçüm zamanı ve başlıkları yerel, Git'e alınmayan `.lymyt/cloudflare-public-baseline.json` içinde. Canlı güvenlik düzeltmeleri tamamlanınca bu belge önce/sonra durumlarıyla güncellenecek.

[Cloudflare Security Insights](https://developers.cloudflare.com/security/security-insights/) düzenli taramalar ve sezgisel bulgular kullanır; açık bir bulgu mevcut ayarlarla karşılaştırılmalıdır. Bulgu sayısını azaltmak için çözümlenmemiş bulgular arşivlenmedi.
