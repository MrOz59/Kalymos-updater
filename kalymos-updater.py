import configparser
import os
import shutil
import hashlib
import time
import psutil
import requests
import zipfile
import tempfile
import subprocess
import tkinter as tk
from tkinter import messagebox
from datetime import datetime

def is_application_running(executable_name):
    """
    Checks if the application is currently running.

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
    Closes the application if it is running.

    Args:
        executable_name (str): The name of the executable to close.
    """
    for process in psutil.process_iter(['name', 'pid']):
        if process.info['name'] == executable_name:
            print(f"Closing {executable_name}...")
            process.terminate()  # Gracefully terminate the process
            process.wait()  # Wait for the process to terminate
            print(f"{executable_name} has been closed.")
            return True
    return False

def create_base_config(ini_file):
    """
    Creates a base configuration file and notifies the user via a message box.

    Args:
        ini_file (str): The path to the configuration file to create.
    """
    config = configparser.ConfigParser()
    config['config'] = {
        'owner': '<GITHUB_OWNER>',
        'repo': '<GITHUB_REPO>',
        'version': '<CURRENT_VERSION>',
        'main_executable': '<MAIN_EXECUTABLE_NAME>'
    }
    with open(ini_file, 'w') as configfile:
        config.write(configfile)

    # Create a Tkinter window to show a message box
    root = tk.Tk()
    root.withdraw()  # Hide the main Tkinter window
    messagebox.showinfo("File not found", f"The file '{ini_file}' was not found. A base configuration file has been created for editing.")
    root.destroy()  # Close the Tkinter window

def load_config(ini_file):
    """
    Loads the configuration from the ini file or creates a base configuration if the file does not exist.

    Args:
        ini_file (str): The path to the configuration file.

    Returns:
        tuple: A tuple containing repository owner, repository name, current version, and main executable name.
    """
    if not os.path.exists(ini_file):
        create_base_config(ini_file)
        exit(1)  # Exit the program after creating the base configuration file

    config = configparser.ConfigParser()
    config.read(ini_file)
    owner = config['config']['owner']
    repo = config['config']['repo']
    current_version = config['config']['version']
    main_executable = config['config']['main_executable']
    return owner, repo, current_version, main_executable

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

def create_backup(root_folder):
    """
    Creates a backup of the current application folder as a ZIP file with the current date.

    Args:
        root_folder (str): The root folder of the application to backup.
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

def launch_application(executable):
    """
    Launches the main application executable.

    Args:
        executable (str): The name of the main executable to launch.
    """
    try:
        subprocess.Popen([executable])
        print(f"Launched {executable}")
    except Exception as e:
        print(f"Failed to launch {executable}: {e}")

def main():
    """
    Main function to check for updates, download and verify them, and replace the current version with the updated one.
    """
    # Path to the configuration file
    ini_file = 'config.ini'
    owner, repo, current_version, main_executable = load_config(ini_file)

    if is_application_running(main_executable):
        close_application(main_executable)
        print(f"Waiting for {main_executable} to close...")
        time.sleep(20)  # Wait 20 seconds for the application to fully close

    new_version = check_for_updates(owner, repo, current_version)
    if new_version:
        file_url = f"https://github.com/{owner}/{repo}/releases/download/{new_version}/update.zip"
        downloaded_file = 'update.zip'
        
        print("Creating a backup of the current version...")
        root_folder = os.getcwd()
        create_backup(root_folder)
        
        print("Downloading new version...")
        download_file(file_url, downloaded_file)
        
        print("Calculating SHA-256 of the downloaded file...")
        downloaded_sha256 = calculate_sha256(downloaded_file)
        
        print("Verifying file integrity...")
        sha256_url = f"https://github.com/{owner}/{repo}/releases/download/{new_version}/update.zip.sha256"
        response = requests.get(sha256_url)
        response.raise_for_status()
        remote_sha256 = response.text.strip()

        if downloaded_sha256 == remote_sha256:
            print("SHA-256 hash verified successfully.")
            
            print("Extracting the new version...")
            temp_dir = tempfile.mkdtemp()
            extract_zip_file(downloaded_file, temp_dir)
            
            print("Replacing files with the new version...")
            replace_files(temp_dir, root_folder)
            
            print("Removing the ZIP file...")
            os.remove(downloaded_file)
            
            print("Launching the main application...")
            launch_application(main_executable)
        else:
            print("File integrity verification failed!")
    else:
        print("No new version available.")

if __name__ == '__main__':
    main()
