import socket


def anything() -> None:
    # server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(("127.0.0.1", 1234))
        # server_socket.listen(5)
        # conn, addr = server_socket.accept()
        # print(f"conn: {conn}")
        # print("addr: ", addr)
        # print("addr: {}".format(addr))

        while True:
            recv_data = server_socket.recv(1024)
            str_data = recv_data.decode()
            print(str_data)
            break

            # conn.send(recv_data)
            # conn.send(recv_data)
            # if recv_data.decode() == "quit":
            #     break

    # server_socket.close()


if __name__ == "__main__":
    anything()