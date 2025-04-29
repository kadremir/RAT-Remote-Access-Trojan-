# RAT Remote Access Trojan

Bu proje, **DeepSeek**, **PentestGPT** ve **ChatGPT** destekleriyle geliştirilmiştir. Yapay zeka destekli bu araçlar, kodun tasarımı, güvenlik değerlendirmesi ve dokümantasyonunda önemli katkılar sağlamıştır. Böylece hem güvenlik odaklı hem de kullanıcı dostu bir RAT sistemi ortaya çıkmıştır. Python ile geliştirilmiş basit ama güçlü bir Remote Access Trojan (RAT) sistemidir. İki ana bileşenden oluşur: **Server** (sunucu) ve **Client** (istemci). Server, hedef makinelerle bağlantı kurup komutlar gönderirken, Client bu komutları alır ve uygular.

---

## Özellikler

- Çoklu istemci yönetimi  
- SSL desteği (opsiyonel)  
- Dosya upload/download  
- Ekran görüntüsü alma  
- Keylogger başlatma/durdurma ve keylogları alma  
- Komut satırı komutları çalıştırma  
- Otomatik startup (kalıcılık)  
- Platformlar arası destek (Windows, Linux)  

---

## Kurulum ve Kullanım

### 1. Server (Sunucu) Kurulumu

- `server.py` dosyasını Python 3.6+ ortamında çalıştırın.  
- Opsiyonel olarak SSL sertifikası ile güvenli bağlantı sağlayabilirsiniz.  
- Server, gelen istemci bağlantılarını dinler ve komutları konsoldan yönetmenizi sağlar.  

```bash
python server.py
```

Server çalıştığında, aktif istemciler listelenir ve istediğiniz istemciyi seçip komut gönderebilirsiniz.

---

### 2. Client (İstemci) Kurulumu ve EXE Oluşturma

Client, hedef makinede çalışacak ve server ile iletişim kuracaktır.

#### PyInstaller ile EXE oluşturma

Client Python dosyasını `.exe` haline getirmek için PyInstaller kullanabilirsiniz:

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole RATCLIENTDEMO.py
```

- `--onefile`: Tek bir yürütülebilir dosya oluşturur.  
- `--noconsole`: Konsol penceresi olmadan çalıştırır (isteğe bağlı).  

Oluşan `dist/RATCLIENTDEMO.exe` dosyasını hedef makinede çalıştırabilirsiniz.

---

### 3. Client Çalıştırma

- EXE dosyasını hedef makinede çalıştırdığınızda, client otomatik olarak server'a bağlanmaya çalışır.  
- Eğer server çalışmıyorsa, client server'ı otomatik başlatmaya çalışır (aynı makinede ise).  
- Client arka planda çalışır, konsol penceresi gizlenir.  
- Client, startup klasörüne kopyalanarak kalıcılık sağlar.  

---

## Server Komutları ve Kullanımı

Server konsolunda, aktif istemciler listelenir. İstemci seçildikten sonra aşağıdaki komutları kullanabilirsiniz:

| Komut           | Açıklama                                                                                   |
|-----------------|--------------------------------------------------------------------------------------------|
| `exec <komut>`  | İstemci üzerinde komut satırı komutu çalıştırır ve çıktısını gösterir.                      |
| `download <dosya>` | İstemciden belirtilen dosyayı indirir. Dosya `downloads/` klasörüne kaydedilir.          |
| `upload <dosya>` | Server'dan istemciye dosya gönderir.                                                      |
| `screenshot`    | İstemcinin ekran görüntüsünü alır ve `downloads/` klasörüne kaydeder.                      |
| `start_keylogger` | İstemcide keylogger başlatır.                                                             |
| `stop_keylogger` | İstemcide çalışan keylogger'ı durdurur.                                                   |
| `get_keylogs`   | Keylogger tarafından kaydedilen tuş vuruşlarını alır ve `downloads/` klasörüne kaydeder.   |
| `exit`          | İstemci bağlantısını sonlandırır.                                                          |
| `back`          | İstemci seçiminden çıkar, istemci listesine geri döner.                                    |
| `exit` (ana menüde) | Server uygulamasını kapatır.                                                             |

---

## Dizin Yapısı

```
/server.py          # Server kodu
/client.py          # Client kodu
/downloads/         # Server tarafında indirilen dosyalar için klasör
/server.log         # Server log dosyası
/client.log         # Client log dosyası (geçici dizinde)
```

---

## Güvenlik, Yasal Uyarılar ve Etik Kullanım

- Bu proje **sadece eğitim ve araştırma amaçlıdır**.  
- Yetkisiz sistemlerde kullanılması **yasa dışıdır** ve ciddi hukuki yaptırımlara yol açabilir.  
- Kişisel verilerin izinsiz toplanması, keylogger kullanımı ve uzaktan erişim gibi faaliyetler birçok ülkede suçtur.  
- Projeyi kullanmadan önce mutlaka ilgili yasal düzenlemeleri inceleyin ve sadece izinli ortamlarda test edin.  
- Bu yazılımın kötü amaçlı kullanımı nedeniyle oluşabilecek tüm sorumluluk kullanıcıya aittir.  

---


---

## Geliştirme ve Katkı

- Daha gelişmiş kimlik doğrulama ve yetkilendirme eklenebilir.  
- İstemci ve server arasındaki iletişim protokolü geliştirilebilir.  
- Platform desteği genişletilebilir.  
- GUI arayüzü eklenebilir.  

---

## İletişim

Herhangi bir soru veya öneri için issue açabilir veya e-posta ile iletişime geçebilirsiniz.

---
