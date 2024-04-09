import subprocess
import re
import sys

from infiltra.utils import clear_screen, BOLD_RED, BOLD_GREEN, BOLD_YELLOW, BOLD_BLUE, BOLD_CYAN, DEFAULT_COLOR

def check_and_install_ssh_audit():
    try:
        # Check if ssh-audit is installed
        subprocess.run(["ssh-audit", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"{BOLD_GREEN}ssh-audit is installed.")
    except (subprocess.CalledProcessError, FileNotFoundError):
        # ssh-audit is not installed; proceed with installation
        print(f"{BOLD_YELLOW}ssh-audit is not installed. Installing now... Please wait.")
        try:
            subprocess.run(["sudo", "apt", "install", "ssh-audit", "-y"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            print(f"{BOLD_GREEN}ssh-audit installed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"{BOLD_RED}Failed to install ssh-audit: {e}")
            sys.exit(1)
def run_ssh_audit(ip, port=22):
    try:
        clear_screen()
        print(f"\n{BOLD_GREEN}Running SSH-Audit on {ip}:{port}\n")
        result = subprocess.run(["ssh-audit", f"{ip}:{port}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output = result.stdout
        if '[fail]' in output:
            fail_lines = [line for line in output.split('\n') if '[fail]' in line]
            print('\n'.join(fail_lines))
        else:
            print(f"{BOLD_GREEN}No [fail] findings.\n")
            print(f"{BOLD_GREEN}Rerunning ssh-audit for you to take a screenshot...")
            subprocess.run(["ssh-audit", f"{ip}:{port}"])  # This will output directly to the terminal
    except subprocess.CalledProcessError as e:
        print(f"ssh-audit failed: {e}")

def main():
    clear_screen()
    print(f'{BOLD_GREEN} Checking if ssh-audit installed.\n')
    check_and_install_ssh_audit()

    clear_screen()
    print(f'{BOLD_BLUE} SSH-Audit and Parser\n')
    ip_input = input(f"{BOLD_GREEN}Enter the IP address (optionally with port, format IP:port):{DEFAULT_COLOR} ").strip()
    match = re.match(r"(\d{1,3}(?:\.\d{1,3}){3})(?::(\d+))?", ip_input)
    if match:
        ip = match.group(1)
        port = int(match.group(2)) if match.group(2) else 22
        run_ssh_audit(ip, port)
    else:
        print("Invalid IP address format.")

    input(f"\n{BOLD_GREEN}Press Enter to return to the menu...")

if __name__ == "__main__":
    main()
