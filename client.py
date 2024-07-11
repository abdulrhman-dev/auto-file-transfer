
import socket
import os
import json

from tqdm import tqdm


IP = '127.0.0.1'
PORT = 4456
SIZE = 1024
FORMAT = "utf-8"
SEND_LOCATION = 'E:\\Projects\\auto-file-transfer\send'


def list_files_walk(start_path='.'):
    found_files = []
    if (not start_path.endswith('\\')):
        start_path = start_path + '\\'

    for root, dirs, files in os.walk(start_path):
        for file in files:
            if (file.startswith('.')):
                continue
            directory_path = root.replace(start_path, "")
            filepath = os.path.join(directory_path, file)
            found_files.append(
                {'directory_path': directory_path, 'filepath': filepath})

    return found_files


def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((IP, PORT))

    send_files = list_files_walk(SEND_LOCATION)
    for file in send_files:
        read_path = os.path.join(SEND_LOCATION, file['filepath'])
        filesize = os.path.getsize(read_path)

        client.send(json.dumps(
            {'filepath':  file['filepath'], 'directory_path': file['directory_path'], 'filesize': filesize, 'files_len': len(send_files)}).encode(FORMAT))
        print(f"[SERVER] {client.recv(SIZE).decode(FORMAT)}")

        bar = tqdm(range(filesize), f"Sending {
            file['filepath']}", unit="B", unit_scale=True, unit_divisor=SIZE)
        with open(read_path, "rb") as file:
            while True:
                chunk = file.read(SIZE)

                if not chunk:
                    break

                client.sendall(chunk)
                bar.update(len(chunk))

        print(f"[SERVER] {client.recv(SIZE).decode(FORMAT)}")
        bar.close()

    client.close()


if __name__ == "__main__":
    main()
