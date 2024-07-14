
import socket
import os
import sys
import json

from datetime import date
from files import recieve, send


with open('./connections.json', 'r') as f:
    server_list = json.load(f)

SIZE = 1024
FORMAT = "utf-8"


EXPORT_LOCATION = 'E:\\Projects\\auto-file-transfer\\send'


if (len(sys.argv) < 2):
    mode = 'RECIEVE'
else:
    match sys.argv[1]:
        case 'r':
            mode = 'RECIEVE'
        case 's':
            mode = 'SEND'
        case _:
            raise Exception(
                'Mode must be either Recive indicated with the: r or send indicated with the: s')


def main():
    selected_servers = server_list

    if (len(sys.argv) > 2):
        server_index = int(sys.argv[2])
        selected_servers = [server_list[server_index]]
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.settimeout(1)
    for index, SERVER in enumerate(selected_servers, start=0):
        try:
            client.connect((SERVER['ip'], SERVER['port']))

            if (mode == 'RECIEVE'):
                client.send('$send'.encode())
                print(client.recv(SIZE).decode())
                current_date = date.today().strftime('%Y%m-%d')
                recieve(client, EXPORT_LOCATION,
                        SERVER['prefix'], current_date, True)
            elif (mode == 'SEND'):
                client.send('$recieve'.encode())
                print(client.recv(SIZE).decode())

                send_location = os.path.join(EXPORT_LOCATION, 'send')
                send(client, send_location, SERVER['extensions'], True)

            client.close()
            if (index < len(selected_servers) - 1):
                print(f'[CLIENT] Changing server from ip:{
                    SERVER['ip']} to ip:{selected_servers[index + 1]['ip']}')
        except socket.error as msg:
            print(msg)
            if (index < len(selected_servers) - 1):
                print(f'[CLIENT] Changing server from ip:{
                    SERVER['ip']} to ip:{selected_servers[index + 1]['ip']}')
            continue


if __name__ == "__main__":
    main()
