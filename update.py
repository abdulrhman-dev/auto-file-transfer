import psutil
import shutil
import os
import time
import json
import winshell

PROGRAM_NAME = "server.exe"


app_path = os.path.join(os.getenv('LOCALAPPDATA'), 'auto-transfer')

if not os.path.exists(app_path):
    raise Exception(
        "No instance of the program found on this system please install the app first before attempting to run the update program")

with open(os.path.join(app_path, 'settings.json'), 'r') as f:
    settings = json.load(f)

processes_names = [process.name() for process in psutil.process_iter()]

if PROGRAM_NAME in processes_names:
    print(f"[PROGRAM] Exiting {PROGRAM_NAME}...")
    os.popen(f"TASKKILL /F /IM {PROGRAM_NAME}")
    time.sleep(2)

PORT = settings['port']
rule_name = f'TCP Port {PORT}'
rule_exists = False if os.popen(f'netsh advfirewall firewall show rule name="{rule_name}"').readlines()[
    1] == 'No rules match the specified criteria.\n' else True

if not rule_exists:
    print("[FIREWALL] Setting up inbound rule")
    os.popen(f'netsh advfirewall firewall add rule name="{
        rule_name}" dir=in action=allow protocol=TCP localport={PORT}')
    print("[FIREWALL] Setting up outbound rule")
    os.popen(f'netsh advfirewall firewall add rule name="{
        rule_name}" dir=out action=allow protocol=TCP localport={PORT}')

if os.path.exists(PROGRAM_NAME):
    print(f"[PROGRAM] Adding {PROGRAM_NAME} to startup programs")
    startup = os.path.join(winshell.startup(), PROGRAM_NAME)
    server_path = os.path.join(os.getcwd(), PROGRAM_NAME)
    shutil.copy(server_path, startup)

print(f"[PROGRAM] reopening {PROGRAM_NAME}")
os.startfile(os.path.join(winshell.startup(), PROGRAM_NAME))


input('Press any key to exit...')
