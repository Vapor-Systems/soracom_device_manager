# Software Updates

The VST Soracom Device Manager provides a powerful feature for remotely updating the software on your IoT devices. This guide explains how to use this feature safely and effectively.

## Overview

The software update feature allows you to:

- Update device software to the latest version
- Monitor the update process in real-time
- Perform updates on remote devices over cellular connections
- Automatically optimize network settings for updates

## Software Update Process

### Accessing the Update Function

To update a device's software:

1. Navigate to a device list and select a device
2. From the device action menu, select option `2` (Update Device Software)
3. Review the update confirmation message

### Update Confirmation

Before proceeding, the system will display a confirmation message:

```
UPDATE CONFIRMATION
─────────────────────────────────────────────
⚠️ This will update the device software to the latest version.
⚠️ The device will be temporarily offline during the update.
⚠️ This operation cannot be undone.
─────────────────────────────────────────────
Are you sure you want to update [device-name]? (yes/no):
```

Type `yes` to confirm or `no` to cancel.

### Update Process

Once confirmed, the update process follows these steps:

1. **Speed Class Optimization**: The system automatically changes the device's speed class to `s1.fast` for faster downloads
2. **SSH Connection**: A secure SSH connection is established with the device
3. **Compatibility Check**: The system determines whether the device is a CM3 or a CM4
4. **Update Files Preparation**: Any old update files are removed, and new ones are downloaded
5. **Update Execution**: The update script is executed on the device
6. **Automatic Reboot**: The device reboots to complete the update
7. **Speed Class Restoration**: The speed class is reverted to `s1.slow` to conserve data

The entire process is displayed in the terminal with real-time status updates.

### Update Completion

After the update completes:

1. The device will reboot automatically
2. The SSH session will close
3. The speed class will be reverted to the original setting
4. You'll return to the device action menu

## Update Logs and Monitoring

During the update process, you'll see detailed logs in real-time:

```
*** STEP 1: REMOVING OLD UPDATE FILES ***
*** STEP 2: DOWNLOADING UPDATE FILES ***
*** STEP 3: CHANGING TO UPDATE DIRECTORY ***
*** STEP 4: RUNNING THE UPDATE SCRIPT ***
```

These logs help you monitor progress and identify any issues that arise.

### After Updates

- **Verify Success**: Check the device status and new software version
- **Test Functionality**: Verify that the device functions correctly
