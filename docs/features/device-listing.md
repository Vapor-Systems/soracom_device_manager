# Device Listing and Searching

The VST Soracom Device Manager provides powerful capabilities for viewing, filtering, and searching your device inventory. This guide explains how to use these features to efficiently manage your device fleet.

## Device List Overview

The device list provides a comprehensive view of your Soracom devices, showing key information at a glance:

- Device name
- Online/offline status
- Software version
- Last connection time

## Accessing Device Lists

From the main menu, you have several options for accessing device lists:

### All Devices

View all devices regardless of status:

1. From the main menu, select option `1` (View All Devices)
2. The complete device list will be displayed

Example output:
```
ALL DEVICES
─────────────────────────────────────────────
1. CSX-0001 ● Online
2. CSX-0002 ○ Offline
3. CSX-0003 ● Online
...
```

### Online Devices

View only devices that are currently online:

1. From the main menu, select option `2` (View Online Devices)
2. A filtered list of online devices will be displayed

Example output:
```
ONLINE DEVICES
─────────────────────────────────────────────
1. CSX-0001 ● Online
2. CSX-0003 ● Online
...
```

### Offline Devices

View only devices that are currently offline:

1. From the main menu, select option `3` (View Offline Devices)
2. A filtered list of offline devices will be displayed

Example output:
```
OFFLINE DEVICES
─────────────────────────────────────────────
1. CSX-0002 ○ Offline
...
```

## Navigating Device Lists

When viewing device lists, you have the following navigation options:

- Enter a device number (e.g., `1`, `2`) to select that device
- Enter `b` to go back to the main menu

For large device lists, the display is automatically paginated for better readability.

## Searching for Devices

The search function allows you to find specific devices quickly:

1. From the main menu, select option `4` (Search Devices)
2. Enter your search term at the prompt:
   ```
   Enter search term (leave blank to return to main menu):
   ```
3. The results will display any devices matching your search term

### Search Functionality

The search feature matches your search term against:

- Device names
- Software versions
- IMSI
- ICCID
- Tags

## Refreshing Device Data

To ensure you're viewing the most current information:

1. From the main menu, select option `5` (Refresh Device Data)
2. Choose a refresh method:
   - `c` - Use cache if available (faster but potentially less current)
   - `a` - Force refresh from API (slower but guaranteed up-to-date)

## Sorting and Filtering

The device lists are sorted alphabetically by device name by default. The application presents pre-filtered views:

- All devices (no filtering)
- Online devices (filtered by online status)
- Offline devices (filtered by offline status)

## Examples

### Finding All Devices with a Specific Software Version

1. From the main menu, select option `4` (Search Devices)
2. Enter the version number (e.g., `002X`)
3. Review the list of matching devices

### Finding a Specific Device by Name

1. From the main menu, select option `4` (Search Devices)
2. Enter the device name or part of it (e.g., `CSX-0001`)
3. Select the specific device from the search results

## Troubleshooting

### No Devices Shown

If no devices are displayed:

1. Verify your Soracom account has devices registered
2. Check your authentication credentials
3. Try refreshing the device data (option `5` from the main menu)
4. Check your internet connection
