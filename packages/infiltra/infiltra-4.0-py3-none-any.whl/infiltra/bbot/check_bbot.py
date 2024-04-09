# check_bbot.py
import subprocess
from infiltra.utils import clear_screen

def is_bbot_installed():
    try:
        subprocess.run(["pip", "list"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result = subprocess.run(["pip", "list"], capture_output=True, text=True)
        return 'bbot' in result.stdout
    except subprocess.CalledProcessError:
        return False

def install_bbot():
    try:
        subprocess.run(["pip", "install", "bbot"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        print("bbot has been installed successfully.")
    except subprocess.CalledProcessError as e:
        print("An error occurred while installing bbot:", e)

if __name__ == "__main__":
    clear_screen()
    if not is_bbot_installed():
        print("bbot is not installed. Installing now...")
        install_bbot()
    else:
        print("bbot is already installed.")