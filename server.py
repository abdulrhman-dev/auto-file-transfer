import socket
# from tqdm import tqdm
import os
import json

app_path = os.path.join(os.getenv('LOCALAPPDATA'), 'auto-transfer')

with open(os.path.join(app_path, 'settings.json'), 'r') as file:
    settings = json.load(file)


IP = settings['ip']
PORT = int(settings['port'])
WATCH_LOCATION = settings['watch_location']
EXTENSIONS = settings['extensions']
SIZE = 1024
FORMAT = 'utf-8'


def list_files_walk(start_path):
    found_files = []
    if (not start_path.endswith('\\')):
        start_path = start_path + '\\'

    for root, dirs, files in os.walk(start_path):
        for file in files:
            if (file.startswith('.')):
                continue
            if (os.path.splitext(file)[1] in EXTENSIONS):
                directory_path = root.replace(start_path, "")
                filepath = os.path.join(directory_path, file)

                found_files.append(
                    {'directory_path': directory_path, 'filepath': filepath})

    return found_files


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((IP, PORT))
    server.listen()

    while True:
        try:
            conn, addr = server.accept()
            # print(f'{addr} connected')
            send_files = list_files_walk(WATCH_LOCATION)

            for file in send_files:
                read_path = os.path.join(WATCH_LOCATION, file['filepath'])
                filesize = os.path.getsize(read_path)

                conn.send(json.dumps(
                    {'filepath':  file['filepath'], 'directory_path': file['directory_path'], 'filesize': filesize, 'files_len': len(send_files)}).encode(FORMAT))
                recived_json = f"[SERVER] {conn.recv(SIZE).decode(FORMAT)}"
                print(recived_json)

                with open(read_path, "rb") as file:
                    while True:
                        chunk = file.read(SIZE)

                        if not chunk:
                            break

                        conn.sendall(chunk)

                confirmation_msg = f"[SERVER] {conn.recv(SIZE).decode(FORMAT)}"
                # print(confirmation_msg)

            conn.close()
        except:
            conn.close()


if __name__ == "__main__":
    main()
