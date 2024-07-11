
import socket
import os
import sys
import json


from tqdm import tqdm
from datetime import date


SERVER_LIST = [
    {
        'IP': '127.0.0.1',
        'PREFIX': 'ABOOD1'
    },
    {
        'IP': '192.168.1.14',
        'PREFIX': 'ABOOD2'
    }
]

PORT = 4456
SIZE = 1024
FORMAT = "utf-8"

CURRENT_DATE = date.today().strftime('%Y%m-%d')
EXPORT_LOCATION = 'E:\\Projects\\auto-file-transfer\\send'


def main():
    SELECTED_SERVERS = SERVER_LIST

    if (len(sys.argv) > 1):
        SERVER_INDEX = int(sys.argv[1])
        SELECTED_SERVERS = [SERVER_LIST[SERVER_INDEX]]
    for index, SERVER in enumerate(SELECTED_SERVERS, start=0):
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((SERVER['IP'], PORT))

            downloaded_files = None

            while downloaded_files is None or downloaded_files > 0:
                str_value = client.recv(SIZE).decode(FORMAT)
                data = json.loads(str_value)

                if (downloaded_files is None):
                    downloaded_files = data['files_len']

                filepath = data['filepath']
                directory_path = data['directory_path']
                filesize = data['filesize']

                print(f"[+] {filepath} received from the server.")
                client.send(f"received {filepath}".encode(FORMAT))

                bar = tqdm(range(filesize), f"Receiving {
                    filepath}", unit="B", unit_scale=True, unit_divisor=SIZE)

                if not os.path.exists(os.path.join(EXPORT_LOCATION, SERVER['PREFIX'], CURRENT_DATE, directory_path)):
                    os.makedirs(os.path.join(EXPORT_LOCATION,
                                SERVER['PREFIX'], CURRENT_DATE, directory_path))

                accumlated_size = 0
                with open(os.path.join(EXPORT_LOCATION, SERVER['PREFIX'], CURRENT_DATE, filepath), "wb") as f:
                    while True:
                        chunk = client.recv(SIZE)
                        accumlated_size += len(chunk)

                        if not chunk:
                            break

                        f.write(chunk)

                        bar.update(len(chunk))
                        if accumlated_size >= filesize:
                            break
                client.send(
                    f"downloaded {filepath} successfully".encode(FORMAT))
                bar.close()
                downloaded_files -= 1

            client.close()
            break
        except socket.error as msg:
            print(msg)
            if (index < len(SELECTED_SERVERS) - 1):
                print(f'[CLIENT] Changing server from ip:{
                    SERVER['IP']} to ip:{SELECTED_SERVERS[index + 1]['IP']}')
            continue


if __name__ == "__main__":
    main()
