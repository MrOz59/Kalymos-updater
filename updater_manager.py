import configparser
import os
import requests
import subprocess

skip_update_check=False # if True, the application will not install updates for Kalymos-Updater

def load_config(ini_file):
    """
    Loads the updater version from the ini file.
    """
    if not os.path.exists(ini_file):
        raise FileNotFoundError(f"Configuration file '{ini_file}' not found.")
    
    config = configparser.ConfigParser()
    config.read(ini_file)
    updater_version = config['config']['updater_version']
    return updater_version

def check_for_updater_update(updater_version):
    """
    Checks the GitHub API for a new version of the updater.
    """
    url = "https://api.github.com/repos/MrOz59/Kalymos-Updater/releases/latest"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        latest_version = response.json()['tag_name']
        
        if latest_version > updater_version:
            print(f"New updater version available: {latest_version}")
            return latest_version
        else:
            print("You are using the latest updater version.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while checking for updates: {e}")
        return None

def download_file(url, destination):
    """
    Downloads a file from the given URL to the specified destination.
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

def ensure_updater(updater_version):
    """
    Ensures the updater executable is present and up-to-date.
    """
    updater_executable = 'kalymos-updater.exe'
    updater_url = f"https://github.com/MrOz59/Kalymos-Updater/releases/download/{updater_version}/kalymos-updater.exe"
    
    if skip_update_check:
        # Only check if the updater exists and download if not present
        if not os.path.isfile(updater_executable):
            print("Updater executable not found. Downloading...")
            download_file(updater_url, updater_executable)
    else:
        # Check for an update and download if necessary
        if not os.path.isfile(updater_executable):
            print("Updater executable not found. Downloading...")
            download_file(updater_url, updater_executable)
        else:
            print(f"Updater executable '{updater_executable}' found.")
            
            new_version = check_for_updater_update(updater_version)
            if new_version:
                new_updater_url = f"https://github.com/MrOz59/Kalymos-Updater/releases/download/{new_version}/kalymos-updater.exe"
                print("Downloading new updater...")
                download_file(new_updater_url, updater_executable)
                print(f"Updater updated to version {new_version}")

    # Run the updater as administrator
    try:
        subprocess.run(['runas', '/user:Administrator', updater_executable], check=True)
    except Exception as e:
        print(f"Failed to run updater as administrator: {e}")

