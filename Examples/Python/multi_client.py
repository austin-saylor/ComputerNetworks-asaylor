import socket


def main() -> None:
    destaddr = "127.0.0.1"
    destport = 1234
    header_length = 10

    username = input("Enter username: ")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((destaddr, destport))
        s.setblocking(False)

        send_len = len(username)
        s.send(f"{send_len:<{header_length}}{username}".encode())

        while True:
            send_msg = input("Send: ")
            if len(send_msg) > 0:
                send_len = len(send_msg)
                print(f"send_len: {send_len}")
                print(f"{send_len:<{header_length}}{send_msg}".encode())
                s.send(f"{send_len:<{header_length}}{send_msg}".encode())
            try:
                recv_len = int(s.recv(header_length).decode())
                recv_msg = s.recv(recv_len).decode()
                print(f"{recv_msg}")
            except:
                continue


if __name__ == "__main__":
    main()