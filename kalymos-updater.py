import configparser
import os
import shutil
import hashlib
import time
import winreg
import psutil
import requests
import zipfile
import tempfile
import subprocess
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import sys

def is_application_running(executable_name):
    """
    Checks if the specified application is currently running.

    Args:
        executable_name (str): The name of the executable to check.

    Returns:
        bool: True if the application is running, False otherwise.
    """
    for process in psutil.process_iter(['name']):
        if process.info['name'] == executable_name:
            return True
    return False

def close_application(executable_name):
    """
    Attempts to close the specified application if it is running.

    Args:
        executable_name (str): The name of the executable to close.

    Returns:
        bool: True if the application was successfully closed, False otherwise.
    """
    for process in psutil.process_iter(['name', 'pid']):
        if process.info['name'] == executable_name:
            print(f"Closing {executable_name}...")
            process.terminate()  # Gracefully terminate the process
            process.wait()  # Wait for the process to terminate
            print(f"{executable_name} has been closed.")
            return True
    return False

def load_config():
    """
    Retrieves configuration values from the Windows registry and displays an error message if any value is missing.

    Returns:
        dict: A dictionary containing the values from the registry ('Owner', 'Repo', 'Version', 'MainExecutable').
    """
    registry_key = r"Software\KalymosApp"
    required_vars = ['Owner', 'Repo', 'Version', 'MainExecutable']
    config = {}

    # Attempt to retrieve values from the registry
    for var in required_vars:
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, f"{registry_key}\\{var}") as reg_key:
                value, _ = winreg.QueryValueEx(reg_key, "Value")
                if not value:
                    raise FileNotFoundError
                config[var] = value
        except (FileNotFoundError, OSError):
            # Show an error message if any registry key is missing or inaccessible
            root = tk.Tk()
            root.withdraw()  # Hide the main Tkinter window
            messagebox.showerror("Missing Registry Key", f"The registry key for '{var}' is missing or inaccessible. Please ensure all required registry keys are set.")
            root.destroy()  # Close the Tkinter window
            sys.exit(1)  # Exit with an error code

    return config['Owner'], config['Repo'], config['Version'], config['MainExecutable']

def check_for_updates(owner, repo, current_version):
    """
    Checks the GitHub repository for a new release using the GitHub API.

    Args:
        owner (str): The GitHub repository owner.
        repo (str): The GitHub repository name.
        current_version (str): The current version of the application.

    Returns:
        str: The latest version available, or None if there is no update.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        latest_version = response.json()['tag_name']
        
        if latest_version > current_version:
            print(f"New version available: {latest_version}")
            return latest_version
        else:
            print("You are already using the latest version.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while checking for updates: {e}")
        return None
    except ValueError as e:
        print(f"Error decoding JSON response: {e}")
        return None

def download_file(url, destination):
    """
    Downloads a file from the given URL to the specified destination.

    Args:
        url (str): The URL of the file to download.
        destination (str): The destination file path to save the downloaded file.
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(destination, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        print(f"Downloaded file from {url} to {destination}")
        
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while downloading the file: {e}")

def calculate_sha256(file_path):
    """
    Calculates the SHA-256 hash of a file.

    Args:
        file_path (str): The path to the file to calculate the SHA-256 hash for.

    Returns:
        str: The SHA-256 hash of the file.
    """
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

def verify_sha256(file_path, expected_hash_path):
    """
    Verifies the SHA-256 hash of a file against an expected hash.

    Args:
        file_path (str): The path to the file to verify.
        expected_hash_path (str): The path to the file containing the expected SHA-256 hash.

    Returns:
        bool: True if the file's hash matches the expected hash, False otherwise.
    """
    try:
        with open(expected_hash_path, 'r') as hash_file:
            expected_hash = hash_file.read().strip()
        
        file_hash = calculate_sha256(file_path)
        if file_hash == expected_hash:
            print(f"SHA-256 hash verified: {file_hash}")
            return True
        else:
            print(f"Hash mismatch: Expected {expected_hash}, but got {file_hash}")
            return False
    except FileNotFoundError:
        print("Hash file not found.")
        return False
    except Exception as e:
        print(f"Error verifying SHA-256 hash: {e}")
        return False

def check_disk_space(file_size):
    """
    Checks if there is enough disk space available to download and extract the update.

    Args:
        file_size (int): The size of the file to be downloaded, in bytes.

    Returns:
        bool: True if there is enough disk space, False otherwise.
    """
    free_space = shutil.disk_usage('.').free
    if free_space > file_size:
        return True
    else:
        print("Not enough disk space available.")
        return False

def create_backup(root_folder):
    """
    Creates a backup of the current application folder as a ZIP file with the current date.

    Args:
        root_folder (str): The root folder of the application to back up.
    """
    today = datetime.now().strftime('%d-%m-%Y')
    backup_zip = os.path.join(tempfile.gettempdir(), f"backup_{today}.zip")
    
    # Create a zip file backup
    with zipfile.ZipFile(backup_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(root_folder):
            for file in files:
                if not file.endswith('.zip'):  # Exclude existing ZIP files from the backup
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, root_folder))
    
    # Move backup to the root folder
    shutil.move(backup_zip, os.path.join(root_folder, os.path.basename(backup_zip)))
    print(f"Backup created at {os.path.join(root_folder, os.path.basename(backup_zip))}")

def extract_zip_file(zip_file, extract_to):
    """
    Extracts a ZIP file to the specified destination folder.

    Args:
        zip_file (str): The path to the ZIP file to extract.
        extract_to (str): The destination folder to extract the ZIP file to.
    """
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print(f"Extracted {zip_file} to {extract_to}")

def replace_files(source_folder, destination_folder):
    """
    Replaces files in the destination folder with files from the source folder.

    Args:
        source_folder (str): The source folder containing the new version files.
        destination_folder (str): The destination folder to replace files in.
    """
    for root, _, files in os.walk(source_folder):
        for file in files:
            src_file = os.path.join(root, file)
            rel_path = os.path.relpath(src_file, source_folder)
            dst_file = os.path.join(destination_folder, rel_path)
            os.makedirs(os.path.dirname(dst_file), exist_ok=True)
            shutil.move(src_file, dst_file)
    print(f"Files from {source_folder} have replaced files in {destination_folder}")

def launch_application(executable, updated):
    """
    Launches the main application executable in the same process.

    Args:
        executable (str): The name of the main executable to launch.
        updated (bool): Indicates if the application has been updated.
    """
    try:
        if updated:
            # Passa o argumento '--updated' ao executar o aplicativo
            os.execv(executable, [executable, '--updated'])
        else:
            # Executa o aplicativo sem argumentos adicionais
            os.execv(executable, [executable])
    except Exception as e:
        print(f"Failed to launch {executable}: {e}")
        sys.exit(1)

def prompt_for_update():
    """
    Prompts the user with a message box to ask if they want to update now.

    Returns:
        bool: True if the user wants to update, False otherwise.
    """
    root = tk.Tk()
    root.withdraw()  # Hide the main Tkinter window
    response = messagebox.askyesno("Update Available", "A new version is available. Would you like to update now?")
    root.destroy()  # Close the Tkinter window
    return response

def update_registry_version(new_version):
    """
    Updates the 'Version' value in the Windows registry.

    Args:
        new_version (str): The new version to set in the registry.
    """
    registry_key = r"Software\KalymosApp"
    value_name = "Version"

    try:
        print(f"New version to be set: {new_version}")
        # Open the registry key where the 'Version' value is stored
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_key, 0, winreg.KEY_SET_VALUE) as reg_key:
            # Update the 'Version' value
            winreg.SetValueEx(reg_key, value_name, 0, winreg.REG_SZ, new_version)
            print(f"Successfully updated {value_name} to {new_version} in the registry.")
    
    except FileNotFoundError:
        print(f"Registry key {registry_key} not found.")
    except PermissionError:
        print("Permission denied. Please run the script with administrator privileges.")
    except Exception as e:
        print(f"An error occurred while updating the registry: {e}")

def main():
    """
    Main function to check for updates, download and verify them, and replace the current version with the updated one.
    """
    owner, repo, current_version, main_executable = load_config()
    print(main_executable)
    # Check for updates
    latest_version = check_for_updates(owner, repo, current_version)
    if not latest_version:
        launch_application(main_executable, True)
        sys.exit(0)

    # Confirm with user if they want to update
    if not prompt_for_update():
        print("Update cancelled.")
        launch_application(main_executable, True)
        sys.exit(0)
        
    close_application(main_executable)

    # Create a backup of the current application
    create_backup('.')

    # Prepare to download the update
    download_url = f"https://github.com/{owner}/{repo}/releases/download/{latest_version}/update.zip"
    update_zip_path = os.path.join('.', 'update.zip')
    
    # Check disk space before downloading
    file_size = int(requests.head(download_url).headers.get('content-length', 0))
    if not check_disk_space(file_size):
        print("Not enough disk space. Exiting update.")
        sys.exit(1)

    # Download the update
    download_file(download_url, update_zip_path)

    # Verify the downloaded file's SHA-256 hash
    if not verify_sha256(update_zip_path, 'update.zip.sha256'):
        print("SHA-256 hash verification failed. Exiting update.")
        

    # Extract the update to the root folder
    extract_zip_file(update_zip_path, '.')

    # Update registry with the new version
    update_registry_version(latest_version)

    # Launch the updated application
    launch_application(main_executable, True)

if __name__ == '__main__':
    main()
