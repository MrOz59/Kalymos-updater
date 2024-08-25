import configparser
from tkinter import Tk, messagebox
from updater_manager import load_config, ensure_updater

def run_demo_app():
    """
    Runs the demonstration application.
    """
    # Load the configuration
    ini_file = 'config.ini'
    try:
        updater_version = load_config(ini_file)
    except FileNotFoundError as e:
        print(e)
        return

    # Ensure the updater is present and up-to-date
    ensure_updater(updater_version)
    
    # Launch the main demo application
    root = Tk()
    root.withdraw()
    messagebox.showinfo("Demo App", "The demo application is now running.")
    root.destroy()

if __name__ == '__main__':
    run_demo_app()
