import argparse
import configparser
import sys
from tkinter import Tk, messagebox
from updater_manager import load_config, ensure_updater

def run_demo_app():
    """
    Runs the demonstration application to illustrate how to integrate the Kalymos Updater into other applications.

    This function performs the following steps:
    1. Loads the configuration from the 'config.ini' file.
    2. Ensures that the Kalymos Updater is present and up-to-date if --updated is not passed.
    3. Launches a simple Tkinter GUI to indicate that the demonstration application is running.
    
    Detailed steps:
    1. **Configuration Loading**:
       - Reads the configuration from a file named 'config.ini'.
       - Extracts the updater version and the application version from this file.

    2. **Argument Parsing**:
       - Parses command-line arguments to check if the '--updated' flag is present.
       - The '--updated' flag indicates whether the application is being run after an update.

    3. **Updater Check**:
       - If the '--updated' flag is not present, the function will call `ensure_updater` to check if the Kalymos Updater needs to be updated.
       - If an update is needed, the function will print a message indicating that the updater is required and exit the program using `sys.exit(0)`.

    4. **GUI Creation**:
       - If no update is needed or the '--updated' flag is present, the function will create a simple Tkinter window.
       - Displays a message box informing that the demonstration application is running.
       - The Tkinter window is hidden and then destroyed after displaying the message.

    Exception Handling:
    - If the configuration file ('config.ini') is not found, the function will print an error message and exit early.
    
    Usage:
    - Run this script from the command line.
    - Optionally pass the '--updated' flag to indicate that the application is being run after an update.
    - Without the '--updated' flag, the script will check for updates and exit if an update is needed.

    Example:
    - `python demo_app.py` - Runs the application and checks for updates.
    - `python demo_app.py --updated` - Runs the application assuming that it has already been updated.
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

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Kalymos Demo Application')
    parser.add_argument('--updated', action='store_true', help='Indicates that the application has been updated.')
    args = parser.parse_args()
    
    # Check if the --updated argument is passed
    if not args.updated:
        # Skip update check if --updated is not passed
        updater_needed = ensure_updater(updater_version, skip_update_check=False)
        
        if updater_needed:
            # Notify the user that an update is needed and stop further execution
            print("Updater needed. Please restart the application after the updater has run.")
            sys.exit(0)
    
    # Create a Tkinter window for demonstration purposes
    root = Tk()
    root.withdraw()  # Hide the main window
    
    # Show a message box indicating that the demo application is running
    messagebox.showinfo("Demo App", "The demo application is now running.")
    
    # Destroy the Tkinter window
    root.destroy()

if __name__ == '__main__':
    run_demo_app()
