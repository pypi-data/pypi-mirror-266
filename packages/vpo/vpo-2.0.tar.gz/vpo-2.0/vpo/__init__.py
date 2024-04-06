#Copyright (c) 2012-2024 Scott Chacon and others

#Permission is hereby granted, free of charge, to any person obtaining
#a copy of this software and associated documentation files (the
#"Software"), to deal in the Software without restriction, including
#without limitation the rights to use, copy, modify, merge, publish,
#distribute, sublicense, and/or sell copies of the Software, and to
#permit persons to whom the Software is furnished to do so, subject to
#the following conditions:
#
#The above copyright notice and this permission notice shall be
#included in all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
#LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
#OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
#WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

'''
An import for an EasyLife 

\n\ndiscord : https://discord.gg/ftX7tXqrQp
\ngithub : https://github.com/hackiyui/vpimport
\ncreator : yashing2 

\n\n____________________________________________________
\n            The import VPO need import :
\n____________________________________________________
\n
\n                    os
\n                    win32security
\n                    socket
\n                    subprocess
\n                    ctypes
\n                    webbrowser
\n                    requests
\n                    uuid
\n                    sys 
\n                    platform
\n                    wmi
\n                    base64
\n                    random
\n                    string
\n                    time
\n                    datetime
\n                    json as jsond
\n                    binascii
\n                    uuid import uuid4
\n                    hmac
\n                    hashlib
\n                    time import sleep
\n                    datetime import datetime
\n                    pystyle import Colorate, Colors
\n                    pyttsx3
\n____________________________________________________
\n____________________________________________________
\n
\n----------------------------------------------------
\n____________________________________________________
\n                   LICENCE : 
\n____________________________________________________
\n
\nCopyright (c) 2012-2024 Scott Chacon and others
\nPermission is hereby granted, free of charge, to any person obtaining
\na copy of this software and associated documentation files (the
\n"Software"), to deal in the Software without restriction, including
\nwithout limitation the rights to use, copy, modify, merge, publish,
\ndistribute, sublicense, and/or sell copies of the Software, and to
\npermit persons to whom the Software is furnished to do so, subject to
\nthe following conditions:
\n#
\nThe above copyright notice and this permission notice shall be
\nincluded in all copies or substantial portions of the Software.
\n#
\nTHE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
\nEXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
\nMERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
\nNONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
\nLIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
\nOF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
\nWITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
\n
\n____________________________________________________
\n____________________________________________________
'''
from .disc import vp_discord
from .disc import tool_discord

def clear():
    import os
    os.system("cls")

def command(command):
    import os 
    os.system(command)

def getuser():
    import os
    '''For have the name of the user'''
    return os.getlogin()

def getpcname():
    import socket
    '''For have the name of the PC'''
    return socket.gethostname()

def sizecmd():
    import os
    '''For have the Terminal Size'''
    return os.get_terminal_size()

def startpath(path):
    import os
    '''For launch an Path'''
    return os.startfile(path)

def current_path():
    import os
    '''For obtain the current directiory'''
    return os.path.dirname(os.path.abspath(__file__))

def open_a_path(path):
    import subprocess
    '''Open a PATH in a new Window'''
    return subprocess.Popen(path)

def delete(path):
    import os
    '''For Delete an path'''
    return os.remove(path)

def errormsg(error_text):
    import ctypes
    '''For display an Error messagebox'''
    return ctypes.windll.user32.MessageBoxW(0, f"{error_text}", "Error", 1)

def msgbox(text, title):
    import ctypes
    '''For display an personalized MsgBox With title and texte personalize'''
    return ctypes.windll.user32.MessageBoxW(0, f"{text}", f"{title}", 1)

def warningmsg(Warning_texte):
    import ctypes
    '''For display an warning MsgBox'''
    return ctypes.windll.user32.MessageBoxW(0, f"{Warning_texte}", "Warning", 0)

def open_link(link):
    import webbrowser
    '''For open an link in a browser'''
    return webbrowser.open(link)

def get_external_ipv4():
    import requests
    '''For obtain the external IPv4'''
    response = requests.get('https://api.ipify.org').text
    return response

def get_uuid():
    import uuid
    from uuid import uuid4
    '''Obtain the UUID'''
    return uuid.uuid4()

def getallmac():
    import subprocess
    '''Get all mac adress'''
    result = subprocess.check_output(['getmac']).decode('cp1252')
    return result 

def resize_grid(cols,lines):
    import os 
    '''Resize the terminal'''
    os.system(f"mode con: cols={cols} lines={lines}")

def check_hwid():
    import os
    '''Obtain your current HWID'''
    os.system('wmic diskdrive get model, serialnumber')
    print("Disk Drive Serial Number")
    os.system('wmic diskdrive get serialnumber')
    print("CPU")
    os.system('wmic cpu get processorid')
    print("BIOS")
    os.system('wmic bios get serialnumber')
    print("Motherboard")
    os.system('wmic baseboard get serialnumber')
    print("smBIOS UUID")
    os.system('wmic csproduct get uuid')
    os.system('getmac')

def antivm():
        import os 
        import sys 
        import platform
        from uuid import uuid4
        import uuid
        '''For SANDBOX in VirusTotal the sandbox detect the file as not malicious'''
        def check_files_on_desktop(file_names):
            desktop_path = os.path.expanduser("~/Desktop")
            
            for file_name in file_names:
                file_path = os.path.join(desktop_path, file_name)
                if os.path.exists(file_path):
                    sys.exit()

        files_to_check = ["report.doc", "keys.txt", "invoice.doc", "report", "Financial_Report.ppt", "account.xlsx", "passwords.txt"]
        check_files_on_desktop(files_to_check)

        def check_windows_mode():
            mode = platform.system()
            if mode == "MS-DOS":
                sys.exit()

        check_windows_mode()

        allowed_names = ["george", "abby", "WDAGUtilityAccount", "A1vHxfPNYE", "dburns", "a6VtQdc"]

        if os.getlogin().lower in allowed_names:
            sys.exit()

        uuid_value = uuid.uuid4()

        # Check if the UUID is equal to a specific value and exit if true
        if str(uuid_value) == '00000000-0000-0000-0000-000000000000':
            sys.exit()

def get_hardware_info():
    import subprocess
    import wmi
    import platform
    '''Obtain tour Hardware Infomations'''
    def get_windows_edition():
        command = 'wmic os get Caption /value'
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output, error = process.communicate()
        
        if output:
            windows_edition = output.decode('utf-8').strip().split('=')[1]
            return windows_edition
        else:
            return "Edition information not found"
    c = wmi.WMI()
    
    for gpu in c.Win32_VideoController():
        print("Graphics Card Name:", gpu.Name)
    
    for processor in c.Win32_Processor():
        print("Processor Name:", processor.Name)

    system_architecture = platform.architecture()[0]
    print("System Architecture: {}-bit".format(system_architecture))
    return get_windows_edition()

def encrypt_64(text):
    import base64
    """Encode the bytes-like object s using Base64 and return a bytes object.

    Optional altchars should be a byte string of length 2 which specifies an
    alternative alphabet for the '+' and '/' characters.  This allows an
    application to e.g. generate url or filesystem safe Base64 strings.
    """
    encoded_bytes = base64.b64encode(text.encode('utf-8'))
    encrypted_text = encoded_bytes.decode('utf-8')
    return encrypted_text

def decrypt_64(encoded_text):
    import base64
    """Decode the Base64 encoded bytes-like object or ASCII string s.

    Optional altchars must be a bytes-like object or ASCII string of length 2
    which specifies the alternative alphabet used instead of the '+' and '/'
    characters.

    The result is returned as a bytes object.  A binascii.Error is raised if
    s is incorrectly padded.

    If validate is False (the default), characters that are neither in the
    normal base-64 alphabet nor the alternative alphabet are discarded prior
    to the padding check.  If validate is True, these non-alphabet characters
    in the input result in a binascii.Error.
    For more information about the strict base64 check, see:

    https://docs.python.org/3.11/library/binascii.html#binascii.a2b_base64
    """
    decoded_bytes = base64.b64decode(encoded_text)
    decoded_text = decoded_bytes.decode('utf-8')
    return decoded_text

def encrypt_32(text):
    import base64
    """Encode the bytes-like object s using Base32 and return a bytes object.

    Optional altchars should be a byte string of length 2 which specifies an
    alternative alphabet for the '+' and '/' characters.  This allows an
    application to e.g. generate url or filesystem safe Base64 strings.
    """
    encoded_bytes = base64.b32encode(text.encode())
    encoded_string = encoded_bytes.decode()
    return encoded_string

def decrypt_32(encoded_text):
    import base64
    """Decode the Base32 encoded bytes-like object or ASCII string s.

    Optional altchars must be a bytes-like object or ASCII string of length 2
    which specifies the alternative alphabet used instead of the '+' and '/'
    characters.

    The result is returned as a bytes object.  A binascii.Error is raised if
    s is incorrectly padded.

    If validate is False (the default), characters that are neither in the
    normal Base-32 alphabet nor the alternative alphabet are discarded prior
    to the padding check.  If validate is True, these non-alphabet characters
    in the input result in a binascii.Error.
    For more information about the strict base64 check, see:

    https://docs.python.org/3.11/library/binascii.html#binascii.a2b_base64
    """
    decoded_bytes = base64.b32decode(encoded_text)
    decoded_text = decoded_bytes.decode('utf-8')
    return decoded_text

def encrypt_vpbase(text, a_key):
    '''Encrypt with VP BASE'''
    encrypted_message = ""
    for char in text:
        encrypted_char = chr((ord(char) + a_key) % 256)  # Shift the character by the key value
        encrypted_message += encrypted_char
    return encrypted_message

def decrypt_vpbase(text, a_key):
    '''Decrypt with VP BASE'''
    decrypted_message = ""
    for char in text:
        decrypted_char = chr((ord(char) - a_key) % 256)  # Reverse the shift by the key value
        decrypted_message += decrypted_char
    return decrypted_message

def generate_random_password(numbers_characters):
    import string
    import random
    '''Generate an random password'''
    characters = string.ascii_letters + string.digits + '@'
    password = ''.join(random.choice(characters) for i in range(numbers_characters))
    return password

def ip2geo(ip_address):
    import requests
    '''For have the Geolocalisation of an IP'''
    url = f'http://ip-api.com/json/{ip_address}'
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        for key, value in data.items():
            print(f'{key}: {value}')
    else:
        print('Failed to retrieve IP information.')

def precise_date():
    import datetime
    '''For have the precise date : 2024-03-17 10:37:13.197906'''
    date = datetime.now()
    date_now = date.strftime("%d/%m/%Y")
    return date

def date_now():
    import datetime
    '''For have the date exemple: 17/04/2000'''
    date = datetime.now()
    date_now = date.strftime("%d/%m/%Y")
    return date_now

def proxies_scrape(path_download):
    import requests
    '''For get free Proxies'''
    r = requests.get("https://api.proxyscrape.com?request=getproxies&proxytype=http")
    rformat = r.text.strip()
    rformat = rformat.replace("\r", "")
    rlist = list(rformat.split("\n"))
    proxylist = []
    with open(path_download, "wb") as file:
        for proxy in rlist:
            file.write((proxy + "\n").encode())

def title(new_title):  
    import os
    '''For change the title of the page'''
    os.system(f"title {new_title}")

def keyauth_connexion(Name,Ownerid,SecretKey, banner):
    import os
    import platform
    import sys 
    import hashlib
    from .authkey import api
    import time
    import requests
    from pystyle import Colorate, Colors
    '''For create an KeyAuth connexion interface'''

    def clear():
        if platform.system() == 'Windows':
            os.system('cls & title Python Example')
        elif platform.system() == 'Linux':
            os.system('clear')
            sys.stdout.write("\x1b]0;Python Example\x07")
        elif platform.system() == 'Darwin':
            os.system("clear && printf '\e[3J'")
            os.system('''echo - n - e "\033]0;Python Example\007"''')

    def getchecksum():
        md5_hash = hashlib.md5()
        file = open(''.join(sys.argv), "rb")
        md5_hash.update(file.read())
        digest = md5_hash.hexdigest()
        return digest

    def invalid_key_message():
        print("you have entered a false key please have a real key")
        time.sleep(3)
        os._exit(1)

    keyauthapp = api(
        name=Name,
        ownerid=Ownerid,
        secret=SecretKey,
        version="1.0",
        hash_to_check=getchecksum()
    )

    def answer():

        pastebin_url = 'https://raw.githubusercontent.com/hackiyui/discord/main/dicord'
        response = requests.get(pastebin_url)
        disc = response.text
                        
        try:
            print(Colorate.DiagonalBackwards(Colors.purple_to_blue, banner))
            print("")
            print(Colorate.DiagonalBackwards(Colors.red_to_green, "creator: " + disc))
            print("")
            key = input(Colorate.DiagonalBackwards(Colors.purple_to_blue, "\n\nEnter your key>>"))
            keyauthapp.license(key)
        except KeyboardInterrupt:
            os._exit(1)
        else:
            pass

    answer()

def python_install(version):
    import requests
    import subprocess
    '''this def permet you too install python with path
    version of python:
    3.11.8 |
3.12.2 |
3.12.1 |
3.11.7 |
3.12.0 |
3.11.6 |
3.11.5 |
3.10.13 |
3.9.18 |
3.8.18 |
3.10.12|
3.11.4 |
3.7.17 |
3.8.17 |
3.9.17 |
3.10.11|
3.11.3 |
3.10.10|
3.11.2 |
3.11.1 |
3.10.9 |
3.9.16 |
3.8.16 |
3.7.16 |
3.11.0 |
3.9.15 |
3.8.15 |
3.10.8 |
3.7.15 |
3.7.14 |
3.8.14 |
3.9.14 |
3.10.7 |
3.10.6 |
3.10.5 |
3.9.13 |
3.10.4 |
3.9.12 |
3.10.3 |
3.9.11 |
3.8.13 |
3.7.13 |
3.9.10 |
3.10.2 |
3.10.1 |
3.9.9 |
3.9.8 |
3.10.0 |
3.7.12 |
3.6.15 |
3.9.7 |
3.8.12 |
3.9.6 |
3.8.11 |
3.6.14 |
3.7.11 |
3.9.5 |
3.8.10 |
3.9.4 |
3.8.9 |
3.9.2 |
3.8.8 |
3.6.13 |
3.7.10 |
3.8.7 |
3.9.1 |
3.9.0 |
3.8.6 |
3.5.10 |
3.7.9 |
3.6.12 |
3.8.5 |
3.8.4 |
3.7.8 |
3.6.11 |
3.8.3 |
2.7.18 |
3.7.7 |
3.8.2 |
3.8.1 |
3.7.6 |
3.6.10 |
3.5.9 |
3.5.8 |
2.7.17 |
3.7.5 |
3.8.0 |
3.7.4 |
3.6.9 |
3.7.3 |
3.4.10 |
3.5.7 |
2.7.16 |
3.7.2 |
3.6.8 |
3.7.1 |
3.6.7 |
3.5.6 |
3.4.9 |
3.7.0 |
3.6.6 |
2.7.15 |
3.6.5 |
3.4.8 |
3.5.5 |
3.6.4 |
3.6.3 |
3.3.7 |
2.7.14 |
3.4.7 |
3.5.4|
3.6.2|
3.6.1 |
3.4.6 |
3.5.3 |
3.6.0 |
2.7.13 |
3.4.5 |
3.5.2 |
2.7.12 |
3.4.4 |
3.5.1 |
2.7.11 |
3.5.0 |
2.7.10 |
3.4.3 | 
2.7.9 | 
3.4.2 | 
3.3.6 | 
3.2.6 | 
2.7.8 | 
2.7.7 | 
3.4.1 | 
3.4.0 | 
3.3.5 | 
3.3.4 | 
3.3.3 | 
2.7.6 | 
2.6.9 | 
3.2.5 | 
3.3.2 | 
2.7.5 | 
3.2.4 | 
2.7.4 | 
3.3.1 | 
3.3.0 | 
3.2.3 | 
2.6.8 | 
2.7.3 | 
3.1.5 | 
3.2.2 | 
3.2.1 | 
2.7.2 | 
3.1.4 | 
2.6.7 | 
2.5.6 | 
3.2.0 | 
3.1.3 | 
2.7.1 | 
2.6.6 | 
2.7.0 | 
3.1.2 | 
2.6.5 | 
2.5.5 | 
2.6.4 | 
2.6.3 | 
3.1.1 | 
3.1.0 | 
2.6.2 | 
3.0.1 | 
2.5.4 | 
2.4.6 | 
2.5.3 | 
2.6.1 | 
3.0.0 | 
2.6.0 | 
2.3.7 | 
2.4.5 | 
2.5.2 | 
2.5.1 | 
2.3.6 | 
2.4.4 | 
2.5.0 | 
2.4.3 | 
2.4.2 | 
2.4.1 | 
2.3.5 | 
2.4.0 | 
2.3.4 | 
2.3.3 | 
2.3.2 | 
2.3.1 | 
2.3.0 | 
2.2.3 | 
2.2.2 | 
2.2.1 | 
2.1.3 | 
2.2.0 | 
2.0.1 |'''

    def install_python(version):
        url = f"https://www.python.org/ftp/python/{version}/python-{version}-amd64.exe"
        response = requests.get(url)
        with open(f"python-{version}-installer.exe", "wb") as file:
            file.write(response.content)

        subprocess.run([f"python-{version}-installer.exe", "/quiet", "InstallAllUsers=1", "PrependPath=1", "en", "python"])
    
    all_versions = [
    "3.11.8", "3.12.2", "3.12.1", "3.11.7", "3.12.0", "3.11.6", "3.11.5", "3.10.13",
    "3.9.18", "3.8.18", "3.10.12", "3.11.4", "3.7.17", "3.8.17", "3.9.17", "3.10.11",
    "3.11.3", "3.10.10", "3.11.2", "3.11.1", "3.10.9", "3.9.16", "3.8.16", "3.7.16",
    "3.11.0", "3.9.15", "3.8.15", "3.10.8", "3.7.15", "3.7.14", "3.8.14", "3.9.14",
    "3.10.7", "3.10.6", "3.10.5", "3.9.13", "3.10.4", "3.9.12", "3.10.3", "3.9.11",
    "3.8.13", "3.7.13", "3.9.10", "3.10.2", "3.10.1", "3.9.9", "3.9.8", "3.10.0",
    "3.7.12", "3.6.15", "3.9.7", "3.8.12", "3.9.6", "3.8.11", "3.6.14", "3.7.11",
    "3.9.5", "3.8.10", "3.9.4", "3.8.9", "3.9.2", "3.8.8", "3.6.13", "3.7.10",
    "3.8.7", "3.9.1", "3.9.0", "3.8.6", "3.5.10", "3.7.9", "3.6.12", "3.8.5",
    "3.8.4", "3.7.8", "3.6.11", "3.8.3", "2.7.18", "3.7.7", "3.8.2", "3.8.1",
    "3.7.6", "3.6.10", "3.5.9", "3.5.8", "2.7.17", "3.7.5", "3.8.0", "3.7.4",
    "3.6.9", "3.7.3", "3.4.10", "3.5.7", "2.7.16", "3.7.2", "3.6.8", "3.7.1",
    "3.6.7", "3.5.6", "3.4.9", "3.7.0", "3.6.6", "2.7.15", "3.6.5", "3.4.8",
    "3.5.5", "3.6.4", "3.6.3", "3.3.7", "2.7.14", "3.4.7", "3.5.4", "3.6.2",
    "3.6.1", "3.4.6", "3.5.3", "3.6.0", "2.7.13", "3.4.5", "3.5.2", "2.7.12",
    "3.4.4", "3.5.1", "2.7.11", "3.5.0", "2.7.10", "3.4.3", "2.7.9", "3.4.2",
    "3.3.6", "3.2.6", "2.7.8", "2.7.7", "3.4.1", "3.4.0", "3.3.5", "3.3.4",
    "3.3.3", "2.7.6", "2.6.9", "3.2.5", "3.3.2", "2.7.5", "3.2.4", "2.7.4",
    "3.3.1", "3.3.0", "3.2.3", "2.6.8", "2.7.3", "3.1.5", "3.2.2", "3.2.1",
    "2.7.2", "3.1.4", "2.6.7", "2.5.6", "3.2.0", "3.1.3", "2.7.1", "2.6.6",
    "2.7.0", "3.1.2", "2.6.5", "2.5.5", "2.6.4", "2.6.3", "3.1.1", "3.1.0",
    "2.6.2", "3.0.1", "2.5.4", "2.4.6", "2.5.3", "2.6.1", "3.0.0", "2.6.0",
    "2.3.7", "2.4.5", "2.5.2", "2.5.1", "2.3.6", "2.4.4", "2.5.0", "2.4.3",
    "2.4.2", "2.4.1", "2.3.5", "2.4.0", "2.3.4", "2.3.3", "2.3.2", "2.3.1",
    "2.3.0", "2.2.3", "2.2.2", "2.2.1", "2.1.3", "2.2.0", "2.0.1"
    ]

    for version in all_versions:
        install_python(version)

def scan_url(api_key, url_to_scan):
    import requests
    '''This it's for scan an URL with VirusTotal but You need an VirusTotal Api Key
        \nUsage:
        \nvpo.scan_url('your_api_key', 'url_to_scan')
    '''
    def scan(url):
        url_scan = 'https://www.virustotal.com/vtapi/v2/url/scan'
        params = {'apikey': api_key, 'url': url}
        response_scan = requests.post(url_scan, data=params)
        scan_id = response_scan.json()['scan_id']
        return scan_id

    def report(scan_id):
        url_report = 'https://www.virustotal.com/vtapi/v2/url/report'
        params = {'apikey': api_key, 'resource': scan_id}
        response_report = requests.get(url_report, params=params)
        return response_report.json()

    def main():
        print("\033[2K\033[1A", end='')

        scan_id = scan(url_to_scan)
        report_results = report(scan_id)

        print("\033[94mScan ID:", scan_id)
        print("\033[92mScan Date:", report_results.get('scan_date'))
        if report_results.get('positives') > 5:
            print("\033[91mTotal number of engines detecting viruses:", report_results.get('positives'))
        else:
            print("\033[93mTotal number of engines detecting viruses:", report_results.get('positives'))

        most_detected_virus = max(report_results.get('scans'), key=lambda x: report_results.get('scans')[x].get('detected', 0))
        most_detected_virus_name = most_detected_virus
        most_detected_antivirus = report_results.get('scans')[most_detected_virus]['result']
        
        ignore_results = ['clean site', 'unrated site']

        if most_detected_antivirus.lower() not in ignore_results:
            print("\033[97m")
            print("_________________________VP MOST______________________")
            print("|                                                      ")
            print(f"|     Most detected Virus: {most_detected_antivirus}    ")
            print(f"|     Antivirus: {most_detected_virus_name}             ")
            print("|______________________________________________________")


        print("\033[91m\n______________________VP scan to VT_____________________")
        print("|                                                      |")
        print("|                All detected viruses                  |")
        print("|______________________________________________________|")
        for engine, result in report_results.get('scans').items():
            if result.get('result').lower() not in ignore_results:
                print("|                                                      ")
                print("|     Virus:", result.get('result'))
                print("|     Antivirus:", engine)
                print("|_______________________________________________________")

        if report_results.get('positives') > 5:
            print("\033[91m\n____________________VP URL SCANNED:_____________________")
            print("|")
            print(f"| {report_results.get('url')}")
            print("|")
            print("|_______________________________________________________")
        elif report_results.get('positives') > 0:
            print("\033[93m\n____________________VP URL SCANNED:_____________________")
            print("|")
            print(f"| {report_results.get('url')}")
            print("|")
            print("|_______________________________________________________")
        else:
            print("\033[92m\n____________________VP URL SCANNED:_____________________")
            print("|")
            print(f"| {report_results.get('url')}")
            print("|")
            print("|_______________________________________________________")

        print("\033[97m")
        print("")
        print("\n__________________VP Finish Message:_____________________")
        print("|")
        print(f"| {report_results.get('verbose_msg')}")
        print("|________________________________________________________")
        print("\033[0m")
    main()

def scan_file(api_key, file_path):
    import requests
    '''This is for scanning a file with VirusTotal but you need a VirusTotal API Key
        \nUsage:
        \nvpo.scan_file('your_api_key', 'file_path_to_scan')
    '''
    def scan_file(file_path):
        url_scan = 'https://www.virustotal.com/vtapi/v2/file/scan'
        params = {'apikey': api_key}
        files = {'file': (file_path, open(file_path, 'rb'))}
        response_scan = requests.post(url_scan, files=files, params=params)
        scan_id = response_scan.json()['scan_id']
        return scan_id

    def report_file(scan_id):
        url_report = 'https://www.virustotal.com/vtapi/v2/file/report'
        params = {'apikey': api_key, 'resource': scan_id}
        response_report = requests.get(url_report, params=params)
        return response_report.json()

    def main():
        print("\033[2K\033[1A", end='')

        scan_id = scan_file(file_path)
        report_results = report_file(scan_id)

        print("\033[94mScan ID:", scan_id)
        print("\033[92mScan Date:", report_results.get('scan_date'))
        if report_results.get('positives') > 5:
            print("\033[91mTotal number of engines detecting viruses:", report_results.get('positives'))
        else:
            print("\033[93mTotal number of engines detecting viruses:", report_results.get('positives'))

        most_detected_virus = max(report_results.get('scans'), key=lambda x: report_results.get('scans')[x].get('detected', 0))
        most_detected_virus_name = most_detected_virus
        most_detected_antivirus = report_results.get('scans')[most_detected_virus]['result']
        
        ignore_results = ['clean site', 'unrated site']

        if most_detected_antivirus.lower() not in ignore_results:
            print("\033[97m")
            print("_________________________VP MOST______________________")
            print("|                                                      ")
            print(f"|     Most detected Virus: {most_detected_antivirus}    ")
            print(f"|     Antivirus: {most_detected_virus_name}             ")
            print("|______________________________________________________")


        print("\033[91m\n______________________VP scan to VT_____________________")
        print("|                                                      |")
        print("|                All detected viruses                  |")
        print("|______________________________________________________|")
        for engine, result in report_results.get('scans').items():
            if result.get('result').lower() not in ignore_results:
                print("|                                                      ")
                print("|     Virus:", result.get('result'))
                print("|     Antivirus:", engine)
                print("|_______________________________________________________")

        if report_results.get('positives') > 5:
            print("\033[91m\n____________________VP File SCANNED:____________________")
            print("|")
            print(f"| {file_path}")
            print("| Dangerous")
            print("|_______________________________________________________")
        elif report_results.get('positives') > 0:
            print("\033[93m\n____________________VP File SCANNED:____________________")
            print("|")
            print(f"| {file_path}")
            print("| not dangerous")
            print("|_______________________________________________________")
        else:
            print("\033[92m\n____________________VP File SCANNED:____________________")
            print("|")
            print(f"| {file_path}")
            print("| Don't open it's really dangerous")
            print("|_______________________________________________________")

        print("\033[97m")
        print("")
        print("\n__________________VP Finish Message:_____________________")
        print("|")
        print(f"| {report_results.get('verbose_msg')}")
        print("|________________________________________________________")
        print("\033[0m")

    main()

def search_virustotal(api_key, resource_type, entry):
    import requests
    '''This is for searching on VirusTotal using the search API
        \nUsage:
        \nvpo.search_virustotal(api_key, resource_type='url', entry='example.com')
        \nvpo.search_virustotal(api_key, 'ip_address', '192.168.1.1')
        \nvpo.search_virustotal(api_key, 'domain', 'example.com')
        \nvpo.search_virustotal(api_key, 'hash', 'abcdef1234567890')

    '''
    def search(resource_type, entry):
        url_search = 'https://www.virustotal.com/vtapi/v2/search'
        params = {'apikey': api_key, 'query': entry, 'resource': resource_type}
        response_search = requests.get(url_search, params=params)
        return response_search.json()

    def main():
        print("\033[2K\033[1A", end='')

        search_results = search(resource_type, entry)

        if search_results.get('response_code') == 1:
            print("\033[92mSearch Results for:", entry)
            print("\033[97m")
            for result in search_results.get('results'):
                print("_________________________Search Result______________________")
                print("|")
                print("|     Type:", result.get('type'))
                print("|     Resource:", result.get('id'))
                print("|     Score:", result.get('reputation'))
                print("|     Last Analysis Date:", result.get('last_analysis_date'))
                print("|___________________________________________________________")
            print("\033[0m")
        else:
            print("\033[91mNo results found for:", entry)
            print("\033[0m")

    main()

def change_paper(image_path):
    import ctypes
    '''Change your wallpaper with an image path'''
    try:
        # Set the image as the wallpaper
        ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 3)
        return 'Wallpaper changed successfully!'
    except Exception as e:
        return str(e)
    
def check_file(file_path):
    '''Check if a file exists with the given path'''
    try:
        with open(file_path, 'r') as file:
            return True
    except FileNotFoundError:
        return False

def speech(text):
    import pyttsx3
    '''Speech a text'''
    engine = pyttsx3.init()
    engine.setProperty('volume', 1.0)
    engine.say(text)
    engine.runAndWait()

def active_windows():
    import os
    '''Activate your windows OS with an KMS key'''
    Home = "TX9XD-98N7V-6WMQ6-BX7FG-H8Q99"
    HomeN = "3KHY7-WNT83-DGQKR-F7HPR-844BM"
    HSL = "7HNRX-D7KGG-3K4RQ-4WPJ4-YTDFH"
    HCS = "PVMJN-6DFY6–9CCP6–7BKTT-D3WVR"
    Pro = "W269N-WFGWX-YVC9B-4J6C9-T83GX"
    ProN = "MH37W-N47XK-V7XM9-C7227-GCQG9"
    Edu = "NW6C2-QMPVW-D7KKK-3GKT6-VCFB2"
    EduN = "2WH4N-8QGBV-H22JP-CT43Q-MDWWJ"
    Ent = "NPPR9-FWDCX-D2C8J-H872K-2YT43"
    EntN = "DPH2V-TTNVB-4X9Q3-TJR4H-KHJW4"

    current_version = os.system("slmgr /dli")

    if current_version == Home:
        os.system(f"slmgr /ipk {Home}")
    elif current_version == HomeN:
        os.system(f"slmgr /ipk {HomeN}")
    elif current_version == HSL:
        os.system(f"slmgr /ipk {HSL}")
    elif current_version == HCS:
        os.system(f"slmgr /ipk {HCS}")
    elif current_version == Pro:
        os.system(f"slmgr /ipk {Pro}")
    elif current_version == ProN:
        os.system(f"slmgr /ipk {ProN}")
    elif current_version == Edu:
        os.system(f"slmgr /ipk {Edu}")
    elif current_version == EduN:
        os.system(f"slmgr /ipk {EduN}")
    elif current_version == Ent:
        os.system(f"slmgr /ipk {Ent}")
    elif current_version == EntN:
        os.system(f"slmgr /ipk {EntN}")

    os.system("slmgr /skms kms8.msguides.com")
    os.system("slmgr /ato")

def restart(time):
    import os 
    '''Permet you to restart pc '''
    os.system(f"shutdown /r /t {time}")

def shutdown(time):
    import os
    '''Permet you to shutdown pc'''
    os.system(f"shutdown /s /t {time}")

def cpu_core():
    import os
    return os.cpu_count()

def close(file_path):
    import os
    file_descriptor = os.open(file_path, os.O_RDWR)

    os.close(file_descriptor)

def kill(pid):
    import os
    import signal
    os.kill(pid, signal.SIGKILL)