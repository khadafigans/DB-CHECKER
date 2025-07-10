import os
from datetime import datetime

def parse_input_file(input_path):
    entries = []
    current_entry = {}
    
    with open(input_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            # New entry starts with "URL:"
            if line.startswith("URL:") and current_entry:
                entries.append(current_entry)
                current_entry = {}
            
            # Parse key-value pairs (e.g., "HOST: xyz")
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip().upper()  # Normalize keys
                value = value.strip().strip('"')
                
                # Map variations to standard keys
                if key in ["HOST", "DB_HOST"]:
                    current_entry["DB_HOST"] = value
                elif key in ["DATABSE", "DB_NAME", "DATABASE"]:
                    current_entry["DB_DATABASE"] = value
                elif key in ["USERNAME", "DB_USER", "USER"]:
                    current_entry["DB_USERNAME"] = value
                elif key in ["PASSWORD", "DB_PASS", "PASS"]:
                    current_entry["DB_PASSWORD"] = value
                elif key in ["PORT", "DB_PORT"]:
                    current_entry["DB_PORT"] = value
                elif key == "METHOD":
                    current_entry["METHOD"] = value
                elif key == "URL":
                    current_entry["URL"] = value
    
    if current_entry:
        entries.append(current_entry)
    
    return entries

def convert_to_env_format(entry):
    env = {
        "URL": entry.get("URL", ""),
        "DB_CONNECTION": "mysql",  # Default
        "DB_HOST": entry.get("DB_HOST", "127.0.0.1"),
        "DB_PORT": entry.get("DB_PORT", "3306"),
        "DB_DATABASE": entry.get("DB_DATABASE", ""),
        "DB_USERNAME": entry.get("DB_USERNAME", ""),
        "DB_PASSWORD": entry.get("DB_PASSWORD", ""),
    }
    
    # Append "/.env" to URL if METHOD is "/.env"
    if "METHOD" in entry and entry["METHOD"] == "/.env":
        env["URL"] = f"{env['URL'].rstrip('/')}/.env"
    
    return env

def write_output_file(entries, output_path):
    with open(output_path, 'w') as f:
        for entry in entries:
            env = convert_to_env_format(entry)
            for key, value in env.items():
                f.write(f"{key}: {value}\n")
            f.write("\n")  # Single newline between entries

def main():
    input_file = input("Please input your file: ").strip()
    
    if not os.path.exists(input_file):
        print(f"❌ Error: File '{input_file}' not found.")
        return
    
    os.makedirs("Results", exist_ok=True)
    now = datetime.now().strftime("%Y%m%d_%H%M%S")  # Format: YYYYMMDD_HHMMSS
    output_path = os.path.join("Results", f"converted_{now}.txt")

    entries = parse_input_file(input_file)
    write_output_file(entries, output_path)

    print(f"\n✅ Conversion complete! Output saved to:\n{output_path}")

if __name__ == "__main__":
    main()
