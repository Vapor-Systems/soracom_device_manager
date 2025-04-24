# Authentication with Soracom API

The VST Soracom Device Manager requires authentication with the Soracom API to access and manage your devices. This guide explains the authentication process and available options.

## Authentication Methods

The VST Soracom Device Manager supports authentication using your Soracom account credentials:

1. **Configuration File**
2. **Interactive Input**

## Setting Up Authentication

### Method 1: Configuration File

The VST Soracom Device Manager uses python-dotenv to load environment variables from a `.env` file. You can store your credentials in this file:

1. Create a new `.env` file in the root directory of the project:

```bash
touch .env
```

2. Open the `.env` file in your text editor and add the following (replacing the email and password with your credentials):

```
# SORACOM API credentials
SORACOM_EMAIL=your-email@example.com
SORACOM_PASSWORD=your-password
```

3. Save the file. The application will automatically load these credentials when it starts.

!!! warning
    This method stores your credentials in plain text on disk. Use with caution and ensure the file has appropriate permissions (e.g., `chmod 600 .env`).

### Method 2: Interactive Input

If you don't provide credentials via environment variables or configuration file, the application will prompt you for them:

```
🔐 Soracom Authentication Required
────────────────────────────────────
Email: your-email@example.com
Password: **********
```

This method is secure for regular usage as credentials aren't stored anywhere.

## Authentication Process

When you run the VST Soracom Device Manager, the authentication process follows these steps:

1. Check for credentials in environment variables
2. If not found, check for credentials in the `.env` file
3. If still not found, prompt the user for credentials
4. Authenticate with the Soracom API
5. Store the authentication token for subsequent API calls
6. Automatically log out and release the token on exit

## API Token Management

The VST Soracom Device Manager handles API token management automatically:

- **Token Generation**: Obtained during initial authentication
- **Token Storage**: Securely maintained in memory (not persisted to disk)
- **Token Cleanup**: Properly released during application exit

## Troubleshooting

### Authentication Failures

If you encounter authentication issues:

1. Verify your Soracom account credentials
2. Check your internet connection
3. Ensure you have the correct permissions in your Soracom account
4. Verify that the API endpoints are accessible from your network

Common error messages and their solutions:

| Error Message | Possible Solution |
|---------------|-------------------|
| "Authentication failed with status code: 401" | Invalid email or password |
| "Authentication failed with status code: 403" | Insufficient permissions or account restrictions |
| "Connection error" | Network connectivity issues |

## Next Steps

After successful authentication:

1. Proceed to the [First Steps Guide](first-steps.md) to learn basic usage
2. Explore the [Features Section](../features/device-listing.md) to understand available capabilities
