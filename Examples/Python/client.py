import socket

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    # client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", 1234))

    while True:
        message = input("Enter a message to send: ")
        s.send(message.encode())
        break
        # recv_buffer = s.recv(1024)
        # print(recv_buffer.decode())
        # if message == "quit":
            # break

    # client_socket.close()