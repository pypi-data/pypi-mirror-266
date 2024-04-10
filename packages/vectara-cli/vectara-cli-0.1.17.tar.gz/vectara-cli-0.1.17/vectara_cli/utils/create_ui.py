# create_ui.py
import subprocess

def create_ui():
    try:
        print("Running Vectara Create-UI command...")
        subprocess.check_call(["npx", "@vectara/create-ui"])
        print("Command executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")

if __name__ == "__main__":
    create_ui()
