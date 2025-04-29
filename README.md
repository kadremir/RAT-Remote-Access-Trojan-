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

---

# RAT Remote Access Trojan

This project is developed with the support of **DeepSeek**, **PentestGPT**, and **ChatGPT**. These AI-powered tools have significantly contributed to the design, security assessment, and documentation of the code, resulting in a security-focused yet user-friendly RAT system. It is a simple but powerful Remote Access Trojan (RAT) system developed in Python. It consists of two main components: **Server** and **Client**. The Server connects to target machines and sends commands, while the Client receives and executes these commands.

---

## Features

- Multi-client management  
- Optional SSL support  
- File upload/download  
- Screenshot capture  
- Start/stop keylogger and retrieve keylogs  
- Execute command line commands  
- Automatic startup (persistence)  
- Cross-platform support (Windows, Linux)  

---

## Installation and Usage

### 1. Server Setup

- Run the `server.py` file in a Python 3.6+ environment.  
- Optionally, you can enable secure connections with SSL certificates.  
- The server listens for incoming client connections and allows you to manage commands via the console.  

```bash
python server.py
```

Once running, active clients will be listed, and you can select a client to send commands.

---

### 2. Client Setup and EXE Creation

The client runs on the target machine and communicates with the server.

#### Creating an EXE with PyInstaller

You can convert the client Python file to an executable using PyInstaller:

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole RATCLIENTDEMO.py
```

- `--onefile`: Creates a single executable file.  
- `--noconsole`: Runs without a console window (optional).  

The resulting `dist/RATCLIENTDEMO.exe` can be run on the target machine.

---

### 3. Running the Client

- When you run the EXE on the target machine, the client will automatically try to connect to the server.  
- If the server is not running, the client will attempt to start it automatically (if on the same machine).  
- The client runs in the background with the console window hidden.  
- The client copies itself to the startup folder to maintain persistence.  

---

## Server Commands and Usage

In the server console, active clients are listed. After selecting a client, you can use the following commands:

| Command           | Description                                                                                   |
|-------------------|-----------------------------------------------------------------------------------------------|
| `exec <command>`  | Executes a command line command on the client and shows the output.                           |
| `download <file>` | Downloads the specified file from the client. Saved in the `downloads/` folder.               |
| `upload <file>`   | Uploads a file from the server to the client.                                                 |
| `screenshot`      | Captures a screenshot from the client and saves it in the `downloads/` folder.                |
| `start_keylogger` | Starts the keylogger on the client.                                                          |
| `stop_keylogger`  | Stops the running keylogger on the client.                                                   |
| `get_keylogs`     | Retrieves keystrokes recorded by the keylogger and saves them in the `downloads/` folder.    |
| `exit`            | Terminates the client connection.                                                            |
| `back`            | Exits client selection and returns to the client list.                                       |
| `exit` (main menu)| Closes the server application.                                                               |

---

## Directory Structure

```
/server.py          # Server code
/client.py          # Client code
/downloads/         # Folder for files downloaded from clients
/server.log         # Server log file
/client.log         # Client log file (temporary directory)
```

---

## Security, Legal Warnings, and Ethical Use

- This project is **for educational and research purposes only**.  
- Unauthorized use on systems without permission is **illegal** and may lead to serious legal consequences.  
- Collecting personal data without consent, using keyloggers, and remote access activities are crimes in many jurisdictions.  
- Always review applicable laws and test only in authorized environments.  
- The user is fully responsible for any misuse or malicious use of this software.  

---

## Development and Contributions

- More advanced authentication and authorization can be added.  
- Communication protocol between client and server can be improved.  
- Platform support can be expanded.  
- A GUI interface can be developed.  

---

## Contact

For questions or suggestions, please open an issue or contact via email.

---
