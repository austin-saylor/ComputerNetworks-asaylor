import socket
import select


def main() -> None:
    hostaddr = "127.0.0.1"
    hostport = 1234
    header_length = 10

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((hostaddr, hostport))
        print(f"Bind to {hostaddr}:{hostport}")
        s.listen(5)
        print(f"Now listening")

        client_dict = {}
        sockets_list = [s]
        while True:
            read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)
            for notified_socket in read_sockets:
                # print(f"notified_socket: {notified_socket}")
                if notified_socket == s:
                    conn, addr = notified_socket.accept()
                    # print(f"Connection from {conn}:{addr}")
                    print(f"New connection adding to dictionary")
                    sockets_list.append(conn)
                    num_bytes = int(conn.recv(header_length).decode())
                    print(f"new connection: num_bytes: {num_bytes}")


                    username = conn.recv(num_bytes)
                    print(f"new connection: username: {username}")
                    client_dict[conn] = username.decode()
                else:
                    #Existing connection
                    #recv message to send to others
                    print(f"Existing connection")
                    recv_header = notified_socket.recv(header_length)
                    print(f"recv_header: {recv_header}")
                    recv_header = recv_header.decode()
                    num_bytes = int(recv_header)
                    print(f"DEBUG: num_bytes")

                    recv_message = notified_socket.recv(num_bytes).decode()
                    print(f"{client_dict[notified_socket]}> {recv_message}")
                    for client in client_dict:
                        # print(f"client: {client}")
                        if client == notified_socket:
                            continue
                        send_len = len(f"{client_dict[notified_socket]}> {recv_message}\n")
                        client.send(f"{send_len:<{header_length}}{client_dict[notified_socket]}> {recv_message}\n".encode())


if __name__ == "__main__":
    main()