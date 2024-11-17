import socket
import ssl

# Configuration
HOST = '127.0.0.1'  # Server's IP address
PORT = 8080  # Server's port

def setup_client():
    # Wrapping socket with SSL context
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.load_verify_locations("server.crt")

    # Connect to server
    with socket.create_connection((HOST, PORT)) as sock:
        with context.wrap_socket(sock, server_hostname=HOST) as secure_socket:
            print("Connected to secure server.")
            
            # Send and receive data
            secure_socket.sendall(b"Hello, server! This is a secure client.")
            data = secure_socket.recv(1024)
            print(f"Received from server: {data.decode('utf-8')}")

if __name__ == "__main__":
    setup_client()
