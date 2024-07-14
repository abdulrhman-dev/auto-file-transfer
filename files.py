import json
import os
import contextlib
from tqdm import tqdm
from datetime import date

SIZE = 1024
FORMAT = "utf-8"


@contextlib.contextmanager
def suppress_print(suppress_console):
    if (suppress_console is True):
        with open(os.devnull, "w") as f, contextlib.redirect_stdout(f):
            yield
    yield


def list_files_walk(start_path, extensions):
    found_files = []
    if (not start_path.endswith('\\')):
        start_path = start_path + '\\'

    for root, dirs, files in os.walk(start_path):
        for file in files:
            if (file.startswith('.')):
                continue
            if (os.path.splitext(file)[1] in extensions):
                directory_path = root.replace(start_path, "")
                filepath = os.path.join(directory_path, file)

                found_files.append(
                    {'directory_path': directory_path, 'filepath': filepath})

    return found_files


def recieve(conn, export_location, prefix='', current_date='', log=False):
    with suppress_print(not log):
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

            bar = tqdm(range(filesize), f"Receiving {
                filepath}", unit="B", unit_scale=True, unit_divisor=SIZE)

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

                    bar.update(len(chunk))
                    if accumlated_size >= filesize:
                        break
            conn.send(
                f"downloaded {filepath} successfully".encode(FORMAT))
            bar.close()
            downloaded_files -= 1


def send(conn, watch_location, extensions, log=False):
    with suppress_print(not log):
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
