# Viewing Device Details

The VST Soracom Device Manager provides detailed information about each of your devices. This guide explains how to access and interpret device details.

## Accessing Device Details

To view detailed information about a device:

1. Navigate to a device list (All Devices, Online Devices, or Offline Devices)
2. Select a device by entering its corresponding number
3. From the device action menu, select option `1` (View Device Information)

## Understanding Device Information

The device details screen provides comprehensive information about the selected device, organized into several sections:

### Basic Information

This section displays fundamental device attributes:

- **Status**: Current connection status (Online/Offline)
- **Software Version**: Current version of the device's software
- **Last Seen**: Timestamp of the most recent connection

Example:
```
BASIC INFORMATION
─────────────────────────────────────────────
Status: Online
ℹ S/W Version: CSX-002X
ℹ Last Seen: 2025-04-22 04:09:52
```

### Network Information

This section provides details about the device's network connection:

- **IP Address**: Current IP address assigned to the device
- **ICCID**: Sim Card serial number
- **IMSI**: Mobile Subscriber Number
- **APN**: Mobile carrier gateway

Example:
```
NETWORK INFORMATION
─────────────────────────────────────────────
ℹ IP Address: 10.0.0.2
ℹ ICCID: 8942410231001597402
ℹ IMSI: 295070912835241
ℹ APN: soracom.io
```

### Tags

This section lists all tags associated with the device.

Example:
```
TAGS
─────────────────────────────────────────────
S/W Version: CSX-002X
Notes: Intermittent Connection Issues
name: CSX-XXXX
```

### Timestamps

This section lists all timestamps associated with the device.

Example:
```
TIMESTAMPS
─────────────────────────────────────────────
ℹ Created: 2022-05-10 12:46:00
ℹ Last Modified: 2025-04-22 04:09:52
```

### OTHER INFORMATION

This section lists all other information not mentioned abvoe associdated with the device.

## JSON View

The Soracom Device Manager also provides a JSON view option for more technical users:

1. When viewing device details, press `j` when prompted
2. The complete device information will be displayed in JSON format

Example JSON output:
```json
{
  "imsi": "295050912435741",
  "msisdn": "423648624740",
  "ipAddress": null,
  "operatorId": "OP0071775974",
  "apn": "soracom.io",
  "type": "s1.slow",
  "groupId": "17d9460b-6280-441a-bac6-4c412a3f760b",
  "createdAt": 1652201460236,
  "lastModifiedAt": 1745309292313,
  "expiredAt": null,
  "registeredTime": null,
  "expiryAction": null,
  "terminationEnabled": false,
  "status": "active",
  "tags": {
    "S/W Version": "CSX-002X",
    "name": "CSX-XXXX"
  },
  "sessionStatus": {
    "sessionId": "01JSE8QQ4B0JKY254NY5MFGWQ2",
    "lastUpdatedAt": 1745309392313,
    "imei": "860195754148983",
    "cell": {
      "radioType": "LTE",
      "mcc": 310,
      "mnc": 410,
      "tac": 28686,
      "eci": 212477975
    },
    "ueIpAddress": "10.0.0.2",
    "dnsServers": [
      "100.127.0.53",
      "100.127.1.53"
    ],
    "online": true,
    "placement": {
      "infrastructureProvider": "aws",
      "region": "us-west-2"
    }
  },
  "previousSession": {
    "sessionId": "01JSDTTVZBK9A57393MK9WGDAP",
    "imei": "860195054148983",
    "cell": {
      "radioType": "LTE",
      "mcc": 310,
      "mnc": 410,
      "tac": 28686,
      "eci": 210173954
    },
    "ueIpAddress": "10.0.0.2",
    "dnsServers": [
      "100.127.0.53",
      "100.127.1.53"
    ],
    "subscription": "plan01s",
    "createdTime": 1745294815659,
    "deletedTime": 1745349391047
  },
  "imeiLock": null,
  "speedClass": "s1.slow",
  "simId": "8942310231001597402",
  "moduleType": "trio",
  "plan": 1,
  "iccid": "8942310221051597402",
  "serialNumber": "8942350221001597402",
  "localInfo": {
    "location": {
      "eci": 211056648,
      "tac": 28686,
      "mnc": 410,
      "mcc": 310,
      "radioType": "lte"
    },
    "imsi": "295050915835741",
    "imei": "860195354148983",
    "iccid": "8942310221001597402",
    "createdTime": 1689966588130,
    "status": "updated",
    "lastModifiedTime": 1689966588161
  },
  "subscription": "plan01s",
  "lastPortMappingCreatedTime": 1744207005874,
  "packetCaptureSessions": null,
  "lastModifiedTime": 1745309392313,
  "expiryTime": null,
  "createdTime": 1652201160236,
  "locationRegistrationStatus": {
    "cs": {
      "plmn": "310410",
      "lastModifiedTime": 1744635662601
    },
    "eps": {
      "plmn": "310410",
      "lastModifiedTime": 1744635660113
    }
  }
}
```

This view provides access to all available device data, including any fields not shown in the standard view.

