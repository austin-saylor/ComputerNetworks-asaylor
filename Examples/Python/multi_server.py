import socket
import select


def main() -> None:
    hostaddr = "127.0.0.1"
    hostport = 1234

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.set_sockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((hostaddr, hostport))
        print(f"Bind to {host_addr}:{hostport}")
        s.listen(5)
        print(f"Now listening")

        client_dict = {}
        sockets_list = [s]
        while True:
            read_socket, _, exception_sockets = select.select(sockets_list, [], sockets_list)
            for notified_socket in read_sockets:
                print(f"notified_socket: {notified_socket}")
                if notified_socket == s:
                    conn, addr = notified_socket.accept()
                    print(f"Connection from {conn}:{addr}")
                    print(f"New connection adding to dictionary")
                    sockets_list.append(conn)
                    username = conn.recv(1024)
                    client_dict[conn] = username.decode()
                else:
                    # Existing connection
                    #recv message to send to others
                    print(f"Existing connection")
                    recv_message = notified_socket.recv(1024).decode()
                    print(f"{client_dict[notified_socket]}> {recv_message}")
                    for client in client_dict:
                        if client == notified_socket:
                            continue
                        client.send(f"{client_dict[notified_socket]}> {recv_message}".encode())


if __name__ == "__main__":
    main()
