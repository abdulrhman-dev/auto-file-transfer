
import socket
import os
import json

from tqdm import tqdm


SERVER_LIST = [
    {
        'IP': '127.0.0.1',
        'PREFIX': 'ABOOD1_'
    },
    {
        'IP': '192.168.1.14',
        'PREFIX': 'ABOOD2_'
    }
]

PORT = 4456
SIZE = 1024
FORMAT = "utf-8"
SEND_LOCATION = 'E:\\Projects\\auto-file-transfer\\send'
EXTENSTIONS = ['.xlsx', '.pdf', '.png', '.jpg']


def list_files_walk(start_path, file_prefix):
    found_files = []
    if (not start_path.endswith('\\')):
        start_path = start_path + '\\'

    for root, dirs, files in os.walk(start_path):
        for file in files:
            if (file.startswith('.')):
                continue
            if (os.path.splitext(file)[1] in EXTENSTIONS):
                directory_path = root.replace(start_path, "")
                filepath = os.path.join(directory_path, file)
                server_filepath = os.path.join(
                    directory_path, file_prefix + file)

                found_files.append(
                    {'directory_path': directory_path, 'filepath': filepath, 'server_filepath': server_filepath})

    return found_files


def main():
    for index, SERVER in enumerate(SERVER_LIST, start=0):
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((SERVER['IP'], PORT))

            send_files = list_files_walk(SEND_LOCATION, SERVER['PREFIX'])

            for file in send_files:
                read_path = os.path.join(SEND_LOCATION, file['filepath'])
                filesize = os.path.getsize(read_path)

                client.send(json.dumps(
                    {'filepath':  file['server_filepath'], 'directory_path': file['directory_path'], 'filesize': filesize, 'files_len': len(send_files)}).encode(FORMAT))
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
            break
        except socket.error as msg:
            print(msg)
            if (index < len(SERVER_LIST) - 1):
                print(f'[CLIENT] Changing server from ip:{
                    SERVER['IP']} to ip:{SERVER_LIST[index + 1]['IP']}')
            continue


if __name__ == "__main__":
    main()
