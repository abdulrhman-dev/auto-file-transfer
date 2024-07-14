import os
import socket
import json
import winshell
import shutil

local_hostname = socket.gethostname()
ip_addresses = socket.gethostbyname_ex(local_hostname)[2]
ip = [ip for ip in ip_addresses if ip.startswith("192.")][0]


print("[NETWORKING] Your Computer IP is:" + ip)

print("[FIREWALL] Setting up inbound rule")
os.popen('netsh advfirewall firewall add rule name="TCP Port 4456" dir=in action=allow protocol=TCP localport=4456')
print("[FIREWALL] Setting up outbound rule")
os.popen('netsh advfirewall firewall add rule name="TCP Port 4456" dir=out action=allow protocol=TCP localport=4456')


print("[PROGRAM] Adding server.exe to startup programs")
startup = os.path.join(winshell.startup(), 'server.exe')
server_path = os.path.join(os.getcwd(), 'server.exe')

shutil.copy(server_path, startup)

app_path = os.path.join(os.getenv('LOCALAPPDATA'), 'auto-transfer')

print("[SETTINGS] Creating settings.json")

if not os.path.exists(app_path):
    os.makedirs(app_path)

with open(os.path.join(app_path, 'settings.json'), 'w') as file:
    json.dump({
        "ip": ip,
        "port": 4456,
        "watch_location": os.path.join(app_path, 'files'),
        "extensions": ['.xlsx', '.pdf', '.png', '.jpg']
    }, file)

print("[SETTINGS] Opening settings.json file")
os.startfile(os.path.join(app_path, 'settings.json'))
os.startfile(winshell.startup())

print('[SUCCESS] Successfully setup server on the computer')
input('Press any key to exit...')
