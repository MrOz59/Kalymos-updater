# Kalymos Updater

## Overview

The Kalymos Updater is designed to manage updates for the Kalymos application. It handles checking for new versions, downloading updates, and ensuring that the application is up-to-date. This repository includes the updater script as well as a demo application to demonstrate how the updater works and how it can be integrated into other projects.

## Updater Functionality

### Features

- **Check for Updates**: The updater checks for new versions of itself by querying the GitHub API.
- **Download Updates**: If a new version is available, the updater downloads the latest version.
- **Run as Administrator**: The updater script is designed to be run with administrator privileges to ensure proper installation.

### How It Works

1. **Check for Updates**: The updater queries the GitHub API to get the latest release information. It compares the latest version with the current version specified in the `config.ini` file.
2. **Download and Replace**: If a newer version is found or if the updater executable is missing, it downloads the latest version from GitHub and replaces the existing executable.
3. **Execute Updater**: The updater script then executes the new updater executable with administrator privileges to perform the update.

## Demo Application

### Purpose

The demo application serves as a simple example to show how the Kalymos Updater can be used. It verifies if an update is available, handles downloading the updater if necessary, and launches the updater.

### How to Run

1. Ensure you have the `config.ini` file with the correct configuration.
2. Run the demo application script: `python demo_app.py`.

### Configuration

The `config.ini` file should have the following structure:

```ini
[config]
owner = MrOz59
repo = kalymos
version = v1.4.1
main_executable = kalymos.exe
updater_version = 1.0.0
```

## Integration with Other Applications

### Overview

To integrate the Kalymos Updater into another application, follow these steps:

1. **Include the Updater Script**: Add the `updater_manager.py` script to your project.
2. **Load Configuration**: Use the `load_config` function to read the `config.ini` file and get the current updater version.
3. **Check and Ensure Updater**: Call the `ensure_updater` function to check for updates and ensure that the updater executable is present. Pass `skip_update_check=True` if you only want to check for the existence of the updater without verifying updates.
4. **Run the Updater**: The `ensure_updater` function will handle running the updater with administrator privileges if needed.

### Example Integration

Here’s an example of how to integrate the updater into your application:

```python
import configparser
from updater_manager import load_config, ensure_updater

def run_my_app():
    # Path to the configuration file
    ini_file = 'config.ini'
    
    try:
        updater_version = load_config(ini_file)
    except FileNotFoundError as e:
        print(e)
        return
    
    # Set this to True to skip the update check and only check if the updater executable exists
    skip_update_check = False
    
    # Ensure the updater is present and up-to-date
    ensure_updater(updater_version, skip_update_check=skip_update_check)
    
    # Launch your main application here
    print("Launching the main application...")

if __name__ == '__main__':
    run_my_app()
```

### Note

- The updater uses the GitHub API to check for updates. Ensure that the API URL is correctly set to your repository’s release endpoint.
- The updater should be run with sufficient privileges to replace its own executable.

## License

This project is licensed under a custom License. See the [LICENSE](LICENSE) file for details.

---
