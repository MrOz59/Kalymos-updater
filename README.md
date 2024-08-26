# Kalymos Updater

## Overview

The Kalymos Updater is designed to manage updates for applications. It handles checking for new versions, downloading updates, and applying them. This repository includes the updater script and a demo application to illustrate how to integrate the updater into other projects.

## Updater Functionality

### Features

- **Check for Updates**: Uses the GitHub API to check for new versions of the updater and the main app.
- **Download Updates**: Downloads the update if a newer version is found.
- **Execute Updater**: Runs the updated executable with administrator privileges.

### Update Files

- **Update ZIP**: The new version of the main app should be posted as `update.zip`.
- **SHA-256 Checksum**: The `update.zip.sha256` file contains the SHA-256 hash of the `update.zip` to verify its integrity.

## Demo Application

### Purpose

The demo application shows how to integrate the Kalymos Updater into another project. It demonstrates how to:

1. Retrieve the updater version from `config.ini`.
2. Check for updates to the updater.
3. Download the updater if it’s missing or out-of-date.
4. Launch the updater to perform the update.

### How to Run

1. Ensure you have a `config.ini` file with the correct configuration.
2. Run the demo application script: `python demo_app.py`.

### Configuration

The `config.ini` file should be structured as follows:

```ini
[config]
owner = MrOz59
repo = kalymos
version = v1.4.1
main_executable = kalymos.exe
updater_version = v1.1.0
```

### Handling the `--updated` Argument

When running the demo application or your application, you can use the `--updated` argument to skip the update checks. Here's how this affects the demo app's behavior:

- **Without `--updated` Argument**: The demo app or your app will check for updates for Kalymos Updater and the main app. If updates are needed, it will notify the user and stop running until the updater runs and the application is restarted.

- **With `--updated` Argument**: The demo application or your app will skip the update checks for both the Kalymos Updater and the main application. This argument indicates that the application has already been updated, or that the update was canceled. The application will proceed without performing any update checks.

To run the demo application with the `--updated` argument, use the following command:

```bash
python demo_app.py --updated
```

This argument is used by the Kalymos Updater to signal to the main application whether the update has already occurred or if the update process was canceled. You can modify this logic as needed to suit different use cases.

## Integration with Other Applications

To integrate the Kalymos Updater into your application:

1. **Include the Script Updater**: Add the `update_manager.py` script to your project, or something similar, that can perform the same function, that is, you can make your own scprit in other languages ​​if you prefer, as long as you keep the `config.ini` with the same format and `Kalymos-Updater.exe` is executed at the end. This script is separate from `kalymos-updater.exe` and must be part of the application being updated.
2. **Load Configuration**: Use `load_config` to read the `config.ini` file and get the current updater version.
3. **Check and Ensure Updater**: to check for updates and ensure the updater executable is present. `Set skip_update_check=True` if you want to prevent the Kalymos Updater from checking for updates itself. This means that the updater will not look for new versions of itself, but it will still ensure that the updater executable exists and is up-to-date for the main application to receive updates.

### Example Integration

Here’s a basic example of integrating the updater into your application:

```python
import configparser
import argparse
from update_manager import load_config, ensure_updater

def run_my_app():
    """
    Runs the main application and integrates the Kalymos Updater.

    This function performs the following steps:
    1. Loads the configuration from 'config.ini' to get the updater version.
    2. Ensures the Kalymos Updater is present and up-to-date.
    3. Launches the main application.
    """
    # Path to the configuration file
    ini_file = 'config.ini'
    
    try:
        updater_version, version = load_config(ini_file)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='My Application')
    parser.add_argument('--updated', action='store_true', help='Indicates that the application has been updated.')
    args = parser.parse_args()
    
    # Check if the --updated argument is passed
    if not args.updated:
        # Skip update check if --updated is not passed
        updater_needed = ensure_updater(updater_version, skip_update_check=False)
        
        if updater_needed:
            # Notify the user that an update is needed and stop further execution
            print("Updater needed. Please restart the application after the updater has run.")
            return  # Stop further execution
    
    # Launch your main application here
    print("Launching the main application...")

if __name__ == '__main__':
    run_my_app()
```

### Note

- The `update_manager.py` script is separate from `kalymos-updater.exe` and should be integrated into the application being updated.
- Use the GitHub API to check for updates. Ensure the API URL is correctly set for your repository’s release endpoint.
- The updater script should be executed with sufficient privileges to replace its own executable.

## License

The Kalymos Updater is licensed under a custom license with the following key points:

- **No Commercial Use**: The software cannot be sold, rented, or used for commercial purposes without explicit written permission.
- **Source Code Restrictions**: The source code or parts of it cannot be copied or used without permission. Modifications through collaboration (e.g., pull requests) on GitHub are allowed.
- **Personal Use**: Allowed for personal projects. For use in commercial software, explicit written permission is required.

For the full license terms, please refer to the [LICENSE](LICENSE) file.
