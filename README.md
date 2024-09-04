---

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

## Changes Made

### 1. **Registry Management Improvements**

- **What’s New**: The updater now retrieves configuration values directly from the Windows registry instead of the previous `config.ini` file. This includes the application version, owner, repository, and executable details.
- **Purpose**: Centralizes application settings in the Windows registry for better management and deployment. This change simplifies configuration by removing the need for a separate `config.ini` file.

### 2. **Update Verification Enhancements**

- **SHA-256 Check**:
  - **What’s New**: Added functionality to verify the integrity of the update file using SHA-256 checksums. The script now calculates the SHA-256 hash of the downloaded update and compares it with the hash provided in `update.zip.sha256`.
  - **Purpose**: Ensures that the downloaded update file has not been tampered with or corrupted, improving security and reliability.

- **Disk Space Verification**:
  - **What’s New**: Implemented a check to ensure there is sufficient disk space available before applying the update.
  - **Purpose**: Prevents update failures due to insufficient disk space, ensuring a smoother update process.

### 3. **Backup Creation**

- **What’s New**: Added a backup creation step that compresses the current application folder into a ZIP file before applying the update.
- **Purpose**: Provides a recovery option if something goes wrong during the update process, allowing users to restore their application to its previous state.

### 4. **Update Confirmation**

- **What’s New**: Added a prompt to confirm with the user whether they want to proceed with the update.
- **Purpose**: Gives users control over when to apply updates, allowing them to choose the best time for the update to occur.


### Handling the `--updated` Argument

When running the demo application or your application, you can use the `--updated` argument to skip the update checks. Here's how this affects the demo app's behavior:

- **Without `--updated` Argument**: The demo app or your app will check for updates for Kalymos Updater and the main app. If updates are needed, it will notify the user and stop running until the updater runs and the application is restarted.

- **With `--updated` Argument**: The demo application or your app will skip the update checks for both the Kalymos Updater and the main application. This argument indicates that the application has already been updated, or that the update was canceled. The application will proceed without performing any update checks.

This argument is used by the Kalymos Updater to signal to the main application whether the update has already occurred or if the update process was canceled. You can modify this logic as needed to suit different use cases.

## Integration with Other Applications

To integrate the Kalymos Updater into your application:

1. **Include the Script Updater**: Add the `update_manager.py` script to your project. This script can be replaced with a similar script in another language if preferred, as long as it maintains the same functionality. Ensure the updater executable is called appropriately.
2. **Load Configuration**: Retrieve configuration values from the Windows registry instead of `config.ini`.
3. **Check and Ensure Updater**: Check for updates and ensure the updater executable is present. Set `skip_update_check=True` if you want to prevent the Kalymos Updater from checking for updates itself. This ensures the updater executable is up-to-date for the main application.

### Example Integration

Here’s a basic example of integrating the updater into your application:

```python
import argparse
from update_manager import ensure_updater

def run_my_app():
    """
    Runs the main application and integrates the Kalymos Updater.

    This function performs the following steps:
    1. Loads the configuration from the Windows registry to get the updater version.
    2. Ensures the Kalymos Updater is present and up-to-date.
    3. Launches the main application.
    """
    version = 'v1.5.4'
    os.environ['Version'] = version
    os.environ['SkipUpdate'] = 'False' #Only affects de updater
    os.environ['Updater'] = 'v1.1.1'
    os.environ['Owner'] = 'MrOz59'
    os.environ['Repo'] = 'kalymos'
    os.environ['MainExecutable'] = 'Kalymos.exe'

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='My Application')
    parser.add_argument('--updated', action='store_true', help='Indicates that the application has been updated.')
    args = parser.parse_args()
    
    # Check if the --updated argument is passed
    if not args.updated:
        # Skip update check if --updated is not passed
        updater_needed = ensure_updater()
        
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

---
