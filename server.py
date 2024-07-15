import socket
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

def list_files_walk(start_path, extensions):
    found_files = []
    if (not start_path.endswith('\\')):
        start_path = start_path + '\\'

    for root, dirs, files in os.walk(start_path):
        for file in files:
            if (file.startswith('.') or file.startswith('~$')):
                continue
            if (os.path.splitext(file)[1] in extensions):
                directory_path = root.replace(start_path, "")
                filepath = os.path.join(directory_path, file)

                found_files.append(
                    {'directory_path': directory_path, 'filepath': filepath})

    return found_files


def recieve(conn, export_location, prefix='', current_date='', log=False):
    downloaded_files = None

    while downloaded_files is None or downloaded_files > 0:
        str_value = conn.recv(SIZE).decode(FORMAT)
        data = json.loads(str_value)

        if (downloaded_files is None):
            downloaded_files = data['files_len']

        filepath = data['filepath']
        directory_path = data['directory_path']
        filesize = data['filesize']

        print(f"[+] {filepath} received from the server.")
        conn.send(f"received {filepath}".encode(FORMAT))

        if not os.path.exists(os.path.join(export_location, prefix, current_date, directory_path)):
            os.makedirs(os.path.join(export_location,
                        prefix, current_date, directory_path))

        accumlated_size = 0
        with open(os.path.join(export_location, prefix, current_date, filepath), "wb") as f:
            while True:
                chunk = conn.recv(SIZE)
                accumlated_size += len(chunk)

                if not chunk:
                    break

                f.write(chunk)

                if accumlated_size >= filesize:
                    break
        conn.send(
            f"downloaded {filepath} successfully".encode(FORMAT))
        downloaded_files -= 1


def send(conn, watch_location, extensions, log=False):
    send_files = list_files_walk(watch_location, extensions)

    for file in send_files:
        read_path = os.path.join(watch_location, file['filepath'])
        filesize = os.path.getsize(read_path)

        conn.send(json.dumps(
            {'filepath':  file['filepath'], 'directory_path': file['directory_path'], 'filesize': filesize, 'files_len': len(send_files)}).encode(FORMAT))
        recived_json = f"[+] {conn.recv(SIZE).decode(FORMAT)}"
        print(recived_json)

        with open(read_path, "rb") as file:
            while True:
                chunk = file.read(SIZE)

                if not chunk:
                    break

                conn.sendall(chunk)

        confirmation_msg = f"[+] {conn.recv(SIZE).decode(FORMAT)}"
        print(confirmation_msg)

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((IP, PORT))
    server.listen()

    while True:
        try:
            conn, addr = server.accept()
            print(f'{addr} connected')
            mode = conn.recv(SIZE).decode()
            conn.send(f'[+] Recived Mode of {mode[1:]}'.encode())

            if (mode == '$recieve'):
                recieve(conn, WATCH_LOCATION)
            elif (mode == '$send'):
                send(conn, WATCH_LOCATION, EXTENSIONS)
            conn.close()
        except Exception as e:
            print(e)
            conn.close()


if __name__ == "__main__":
    main()
