import socket
from tqdm import tqdm
import json

IP = socket.gethostbyname(socket.gethostname())
PORT = 4456
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print("[+] Listening...")
    while True:
        conn, addr = server.accept()
        print(f"[+] Client connected from {addr[0]}:{addr[1]}")

        data = json.loads(conn.recv(SIZE).decode(FORMAT))
        FILENAME = data['filename']
        FILESIZE = data['size']

        print("[+] Filename and filesize received from the client.")
        conn.send("Filename and filesize received".encode(FORMAT))

        bar = tqdm(range(FILESIZE), f"Receiving {
            FILENAME}", unit="B", unit_scale=True, unit_divisor=SIZE)

        with open(f"recv_{FILENAME}", "wb") as f:
            while True:
                data = conn.recv(SIZE)

                if not data:
                    break

                f.write(data)
                bar.update(len(data))

        bar.close()
        conn.close()


if __name__ == "__main__":
    main()
