
import socket
import os
import json

from tqdm import tqdm


IP = socket.gethostbyname(socket.gethostname())
PORT = 4456
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
FILENAME = "202407-02-temp.xlsx"
FILESIZE = os.path.getsize(FILENAME)


def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)

    print(f'[CLIENT] Sent file info')
    client.send(json.dumps(
        {'filename': FILENAME, 'size': FILESIZE}).encode(FORMAT))

    msg = client.recv(SIZE).decode(FORMAT)
    print(f"SERVER: {msg}")

    bar = tqdm(range(FILESIZE), f"Sending {
               FILENAME}", unit="B", unit_scale=True, unit_divisor=SIZE)

    with open(FILENAME, "rb") as file:
        while chunk := file.read(SIZE):
            client.send(chunk)
            bar.update(len(chunk))

    bar.close()
    client.close()


if __name__ == "__main__":
    main()
