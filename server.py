import socket
# from tqdm import tqdm
import os
import json

app_path = os.path.join(os.getenv('LOCALAPPDATA'), 'auto-transfer')

if not os.path.exists(app_path):
    os.makedirs(app_path)
    with open(os.path.join(app_path, 'settings.json'), 'w') as file:
        json.dump({
            "ip": "127.0.0.1",
            "port": "4456",
            "export_location": os.path.join(app_path, 'files')
        }, file)
    # print("[+] Created App Directory successfully!")


with open(os.path.join(app_path, 'settings.json'), 'r') as file:
    settings = json.load(file)


IP = settings['ip']
PORT = int(settings['port'])
EXPORT_LOCATION = settings['export_location']
SIZE = 1024
FORMAT = 'utf-8'


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((IP, PORT))
    server.listen()
    # print("[+] Listening...")

    while True:
        try:
            conn, addr = server.accept()
            # print(f"[+] Client connected from {addr[0]}:{addr[1]}")

            downloaded_files = None

            while downloaded_files is None or downloaded_files > 0:
                str_value = conn.recv(SIZE).decode(FORMAT)

                data = json.loads(str_value)

                if (downloaded_files is None):
                    downloaded_files = data['files_len']

                filepath = data['filepath']
                directory_path = data['directory_path']
                filesize = data['filesize']

                # print(f"[+] {filepath} received from the client.")
                conn.send(f"received {filepath}".encode(FORMAT))

                # bar = tqdm(range(filesize), f"Receiving {
                #     filepath}", unit="B", unit_scale=True, unit_divisor=SIZE)

                if not os.path.exists(os.path.join(EXPORT_LOCATION, directory_path)):
                    os.makedirs(os.path.join(EXPORT_LOCATION, directory_path))

                accumlated_size = 0
                with open(os.path.join(EXPORT_LOCATION, filepath), "wb") as f:
                    while True:
                        chunk = conn.recv(SIZE)
                        accumlated_size += len(chunk)

                        if not chunk:
                            break

                        f.write(chunk)

                        # bar.update(len(chunk))
                        if accumlated_size >= filesize:
                            break
                conn.send(f"downloaded {filepath} successfully".encode(FORMAT))
                # bar.close()
                downloaded_files -= 1

            conn.close()
        except:
            conn.close()
            # print('[-] Disconnected the client')


if __name__ == "__main__":
    main()
