# Tag Management

The VST Soracom Device Manager provides a comprehensive system for managing tags on your devices. Tags help you organize, classify, and search for devices efficiently. This guide explains how to manage device tags through the terminal interface.

## Understanding Device Tags

Device tags are key-value pairs associated with a device that provide additional metadata or classification information:

- **Tag Key**: A unique identifier for the tag category (e.g., `notes`, `name`, `S/W Version`)
- **Tag Value**: The specific value for that category (e.g., `Connection issues`, `CSX-0001`, `CSX-002X`)

## Accessing Tag Management

To manage tags for a device:

1. Navigate to a device list and select a device
2. From the device action menu, select option `4` (Manage Device Tags)
3. The tag management interface will be displayed

## Tag Management Interface

The tag management interface displays all current tags and provides options for adding, editing, and deleting tags:

```
DEVICE TAGS
─────────────────────────────────────────────
Current tags for device-001:

1. S/W Version: CSX-002X
2. Notes: Intermittent Connection Issues
3. name: CSX-XXXX

─────────────────────────────────────────────
A. Add a new tag
E. Edit an existing tag
D. Delete a tag
B. Back to device menu
```

## Managing Tags

### Adding a New Tag

To add a new tag:

1. From the tag management interface, select option `A` (Add a new tag)
2. Enter the tag key when prompted:
   ```
   Enter tag key:
   ```
3. Enter the tag value when prompted:
   ```
   Enter tag value:
   ```
4. The system will add the tag and display the updated tag list

Example:
```
Enter tag key: notes
Enter tag value: 'Updated to new version!'
✓ Tag added successfully!
```

### Editing an Existing Tag

To edit an existing tag:

1. From the tag management interface, select option `E` (Edit an existing tag)
2. Enter the number of the tag you want to edit:
   ```
   Enter tag number to edit (1-3):
   ```
3. Enter the new value for the tag:
   ```
   Enter new value for [tag-key]:
   ```
4. The system will update the tag and display the updated tag list

Example:
```
Enter tag number to edit (1-3): 1
Current value: CSX-002K
Enter new value for location: CSX-002L
✓ Tag updated successfully!
```

### Deleting a Tag

To delete a tag:

1. From the tag management interface, select option `D` (Delete a tag)
2. Enter the number of the tag you want to delete:
   ```
   Enter tag number to delete (1-3):
   ```
3. Confirm the deletion:
   ```
   Are you sure you want to delete tag [tag-key]: [tag-value]? (yes/no):
   ```
4. The system will remove the tag and display the updated tag list

Example:
```
Enter tag number to delete (1-3): 3
Are you sure you want to delete tag 'S/W Version'? (yes/no): yes
✓ Tag deleted successfully!
```

## Tag Synchronization

When you add, edit, or delete a tag:

1. The change is immediately synchronized with the Soracom platform
2. The local device record is updated
3. The tag becomes available for searching and filtering

