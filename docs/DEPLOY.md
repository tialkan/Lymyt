# tezatlas.info / Coolify

```text
Mac: Codex + Claude → yerel yardımcı → HTTPS /v1/ingest
                                               ↓
                                     VPS: Lymyt relay
                                      ├── web Studio
                                      └── /v1/status → Nano
                                           /v1/device ← Nano
```

Nano ayrıca Mac yardımcısına doğrudan bağlanabilir; o durumda fiziksel telemetri sadece yerel yardımcıda görünür. VPS'e bağlı Nano için güvenilir TLS kök CA'sı `config.h` içine konmalıdır; sertifika doğrulaması kapatılmaz.

## Bu kurulumun durumu

8 Ekim 2026: [private GitHub reposu](https://github.com/tialkan/Lymyt) ve ayrı Lymyt/production Coolify uygulaması oluşturuldu. Dockerfile dağıtımı `968d5f4` commit'inden tamamlandı. Relay 8787 portunda çalışıyor; named volume `/data` hedefinde bağlı. HTTPS `tezatlas.info` uygulamada ayarlı. Turkticaret oturumu sona erdiği için DNS değişmedi; TLS ve Mac → VPS senkronizasyonu henüz doğrulanmadı.

[Coolify uygulaması](http://157.90.232.143:8000/project/dg4k8gsk84sc84csc84sgsk0/environment/c4cwgwg0kcccwskg8o4go0o4/application/w0wsg0o8woogs8c4cwwkk0s0).

## Coolify

- Proje: Lymyt, ortam: production; kaynak: bu GitHub reposu.
- Build pack: Dockerfile, dosya: `/Dockerfile`, port: `8787`.
- Domain: `https://tezatlas.info`.
- Kalıcı volume: `/data`, UID 10001'in yazabildiği volume.
- Relay komutu Dockerfile içinde hazır. VPS'e Codex/Claude oturumu kurulmaz.
- TLS mevcut Coolify proxy tarafından sağlanır.

Alternatif: `docker compose up -d --build`. Compose sadece VPS localhost:8787'ye bağlanır; mevcut reverse proxy HTTPS üzerinden buraya yönlendirir.

## Anahtarlar

Relay ilk açılışta `/data/device-token` (okuma ve telemetri), `/data/sync-token` (limit yükleme) üretir. Değerler loglara yazılmaz. Kullanıcı sync değerini Mac'te `.lymyt/cloud-sync-token` içine kaydeder ve dosyayı `chmod 600` ile sınırlar.

```sh
python3 bridge/lymyt.py serve \
  --sync-url https://tezatlas.info/v1/ingest \
  --sync-token-file .lymyt/cloud-sync-token
```

Yardımcı ürün, yüzde, pencere süresi, gözlem ve yenilenme zamanlarını gönderir. Relay bilinmeyen alanları atar. Yeni yükleme eski verinin gözlem zamanını değiştirmez. Hesap OAuth tokenları buluta taşınmaz.

## DNS

8 Ekim 2026'da panelde görülen: kök A=`31.186.11.254`, www CNAME=`tezatlas.info` (iki aynı CNAME satırı). Nameserver'lar Turkticaret üzerinde. Hedef VPS doğrulanıp uygulama hazırlandıktan sonra kök A kaydı VPS IP'sine güncellenir.

Yayın doğrulaması: uygulama portu, /data yazımı, TLS, yetkisiz /v1/status isteğinin 401 olması, yerel HTTPS senkronizasyonu. Bu dosyanın bulunması yayının tamamlandığını göstermez.
