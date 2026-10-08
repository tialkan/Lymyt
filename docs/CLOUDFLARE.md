# tezatlas.info / Cloudflare katmanı

8 Ekim 2026'da mevcut Cloudflare hesabında tezatlas.info zone'u Free plan ile oluşturuldu. Kök A kaydı 157.90.232.143 olarak hazırlandı; www CNAME tezatlas.info'ya işaret ediyor. İki kayıtta da proxy açık. **Nameserver devri, HTTPS ve gerçek internet erişimi doğrulanana kadar bu dosya yayının tamamlandığı anlamına gelmez.**

Dış sorguyla eski NS=ns1/ns2/ns3.turkticaret.net ve DS kaydı bulunmadığı doğrulandı. Nameserver değişimi için işlem anında kullanıcı onayı bekleniyor. Cloudflare, aktivasyon tamamlanmadan SSL/TLS sayfasında nameserver adımını gösteriyor.

Atanan nameserver'lar:

```text
annabel.ns.cloudflare.com
ridge.ns.cloudflare.com
```

Bunlar yalnızca bu zone'un panelinde görülen değerlerdir; başka bir domain için kopyalanmaz. Turkticaret üzerinde sadece tezatlas.info'nun nameserver'ları değiştirilir. Eski park kaydı A=31.186.11.254 idi. Tarama bir A ve bir www CNAME buldu; Turkticaret'te iki aynı www satırı görünüyordu. MX/TXT kaydı görünmedi.

## Hedef

```text
Tarayıcı / Nano → HTTPS Cloudflare → HTTPS Coolify proxy → Lymyt relay:8787
Mac yardımcısı  → HTTPS /v1/ingest ──────────────────────┘
```

Cloudflare CDN/DNS/proxy katmanıdır; uygulama Coolify'de çalışır. Mac sağlayıcı limitlerini okur, normalize edilmiş yüzde ve zamanları yükler. Hesap OAuth oturumları VPS'e veya Cloudflare ayarlarına konmaz.

## Yayın kontrolü

1. Registrar nameserver değişimi gerçekten kaydedilmiş olmalı. NS ve DS kayıtları kontrol edilir; eski DNSSEC DS varsa yeni imzayla uyuşmadan yönlendirme yapılmaz.
2. Cloudflare zone durumu Active olmalı; A ve www içerikleri doğru kalmalı.
3. Coolify origin `tezatlas.info` için geçerli sertifika sunmalı. Cloudflare **Full (strict)** seçilir; bu mod origin sertifikasını ve hostname'ini doğrular. [Cloudflare belgesi](https://developers.cloudflare.com/ssl/origin-configuration/ssl-modes/full-strict/).
4. `https://tezatlas.info/` Studio sayfasını 200 ile döndürmeli; sertifika denetimi kapatılmaz.
5. Anahtarsız `/v1/status` ve `/v1/ingest` yetkisiz olmalı. `/v1/*` için Cache Everything uygulanmaz; status yanıtı `Cache-Control: no-store` taşır. API istemcilerine JavaScript challenge gösteren bir kural eklenmez.
6. Relay'in `/data` volume'ü yazılabilir, device-token ve ayrı sync-token kalıcı olmalı. Mac yalnızca sync anahtarı ile upload yapar; Nano/Studio device anahtarı ile okur.
7. Mac'teki upload başarılı olup taze gözlem zamanı buluttan okununca gerçek veri yolu doğrulanır.

522/523 bağlantı hatasında origin IP/port/proxy kontrol edilir. 526 durumunda origin sertifikası ve Full (strict) eşleşmesi kontrol edilir. DNS yayılması bitmeden erişim her ağda aynı anda değişmeyebilir. [Nameserver kurulum belgesi](https://developers.cloudflare.com/dns/zone-setups/full-setup/setup/).
