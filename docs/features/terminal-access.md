# Terminal Access (SSH)

The VST Soracom Device Manager provides secure terminal access to your devices via SSH. This guide explains how to connect to your devices and manage them through the command line.

## Overview

The terminal access feature allows you to:

- Establish secure SSH connections to remote devices
- Execute commands directly on the device
- Perform maintenance and troubleshooting
- Access device logs and configuration files
- Install or configure software manually

## Accessing the Terminal

### Connecting to a Device Terminal

To connect to a device terminal:

1. Navigate to a device list and select a device
2. From the device action menu, select option `3` (Connect to Device Terminal (SSH))
3. The system will attempt to establish an SSH connection

### Connection Process

The connection process involves several steps:

1. **Port Mapping Setup**: The system uses Soracom's Napter service to create a temporary port mapping to your device
2. **SSH Connection**: A secure SSH connection is established using the configured credentials
3. **Authentication**: The system authenticates using the default username and password
4. **Terminal Session**: Once connected, you'll have direct command-line access to your device

## Manual Connection

In some cases, automatic connection may not work. The system will display manual connection instructions:

```
TERMINAL CONNECTION GUIDE
├─ Manual setup instructions
╰──────────────────────────────────────────────
MANUAL CONNECTION STEPS
│ 1. Login to the Soracom User Console
│ 2. Go to SIM Management
│ 3. Find and select the device: [device-name]
│ 4. From the Actions menu, select 'On-demand remote access'
│ 5. Configure the port mapping:
│    • Port: 22
│    • Duration: As needed (maximum 8 hours)
│ 6. After creating the port mapping, note the hostname and port
│ 7. Connect using your SSH client:
│    • SSH command: ssh pi@[hostname] -p [port]
╰──────────────────────────────────────────────
```

Follow these instructions to connect manually using your preferred SSH client.
