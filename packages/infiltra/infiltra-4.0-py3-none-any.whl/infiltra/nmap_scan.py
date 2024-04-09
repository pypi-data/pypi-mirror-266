# nmap_scan.py

import os
import subprocess
import ipaddress
import sys


def is_valid_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def nmap_is_installed():
    return subprocess.run(['which', 'nmap'], stdout=subprocess.PIPE, stderr=subprocess.PIPE).returncode == 0


def run_nmap_scan(ip_list, scan_type, project_path):
    # Create the 'tmp' directory within the project path if it doesn't exist
    tmp_dir = os.path.join(project_path, 'tmp')
    os.makedirs(tmp_dir, exist_ok=True)

    if scan_type not in ["tcp", "udp", "both"]:
        print("Invalid scan type: Choose 'tcp', 'udp', or 'both'.")
        sys.exit(1)

    if not nmap_is_installed():
        print("Nmap is not installed or not found in PATH.")
        sys.exit(1)

    # Prepare command strings
    tcp_scan_command = f"sudo nmap -sSV --top-ports 4000 -Pn -oG tcp.txt {' '.join(ip_list)}"
    udp_scan_command = f"sudo nmap -sU --top-ports 400 -Pn -oG udp.txt {' '.join(ip_list)}"

    # Prepare terminal commands to open new windows
    terminal_command_prefix = "gnome-terminal -- bash -c '"
    terminal_command_suffix = "; read -p \"Press enter to close\"'"

    if scan_type == "tcp" or scan_type == "both":
        tcp_command = terminal_command_prefix + tcp_scan_command + terminal_command_suffix
        subprocess.Popen(tcp_command, shell=True)

    if scan_type == "udp" or scan_type == "both":
        udp_command = terminal_command_prefix + udp_scan_command + terminal_command_suffix
        subprocess.Popen(udp_command, shell=True)


def main():
    if len(sys.argv) < 3:
        print("Usage: nmap_scan.py [single_ip/ip_file_path] [tcp/udp/both] [project_path]")
        sys.exit(1)

    input_arg = sys.argv[1]
    scan_type = sys.argv[2].lower()
    project_path = sys.argv[3]

    try:
        if os.path.isfile(input_arg):
            with open(input_arg, 'r') as file:
                ip_list = file.read().splitlines()
                # Validate IPs in file
                for ip in ip_list:
                    if not is_valid_ip(ip):
                        print(f"Invalid IP found in file: {ip}")
                        sys.exit(1)
            # Run scan with file input
            run_nmap_scan(ip_list, scan_type, project_path)
        elif is_valid_ip(input_arg):
            # Run scan with single IP
            run_nmap_scan([input_arg], scan_type, project_path)
        else:
            print("Invalid input: Please provide a valid single IP or a path to a text file with IPs.")
            sys.exit(1)

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()