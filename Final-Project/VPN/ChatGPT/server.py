import socket
import ssl

# Configuration
HOST = '127.0.0.1'  # localhost
PORT = 8080  # port to bind

def setup_server():
    # Create a TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)  # Listen for up to 5 connections
    print(f"Server started on {HOST}:{PORT}")

    # Wrapping socket with SSL context
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile="server.crt", keyfile="server.key")

    # Accept clients and handle communication
    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection from {addr}")
        secure_socket = context.wrap_socket(client_socket, server_side=True)

        # Receive and send data
        try:
            data = secure_socket.recv(1024)
            print(f"Received from client: {data.decode('utf-8')}")
            secure_socket.sendall(b"Hello, client! This is a secure server.")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            secure_socket.close()

if __name__ == "__main__":
    setup_server()
