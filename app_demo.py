import configparser
from tkinter import Tk, messagebox
from updater_manager import load_config, ensure_updater

def run_demo_app():
    """
    Runs the demonstration application to illustrate how to integrate the Kalymos Updater into other applications.
    
    This function performs the following steps:
    1. Loads the configuration from the 'config.ini' file.
    2. Ensures that the Kalymos Updater is present and up-to-date.
    3. Launches a simple Tkinter GUI to indicate that the demonstration application is running.
    """
    # Define the path to the configuration file
    ini_file = 'config.ini'
    
    try:
        # Load the updater version and application version from the configuration file
        updater_version, version = load_config(ini_file)
    except FileNotFoundError as e:
        # Print an error message if the configuration file is not found
        print(f"Error: {e}")
        return

    # Ensure the Kalymos Updater is present and up-to-date
    # Set skip_update_check to True for demonstration purposes, so no actual update check is performed
    ensure_updater(updater_version, skip_update_check=True)

    # Create a Tkinter window for demonstration purposes
    root = Tk()
    root.withdraw()  # Hide the main window
    
    # Show a message box indicating that the demo application is running
    messagebox.showinfo(f"Demo App version: {version}", "The demo application is now running.")
    
    # Destroy the Tkinter window
    root.destroy()

# Check if the script is being run directly
if __name__ == '__main__':
    run_demo_app()
