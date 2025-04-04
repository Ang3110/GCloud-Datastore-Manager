# Google Cloud Datastore Manager (GCDM) - Setup Documentation

This document explains how to set up the Google Cloud Datastore Manager (GCDM) tool and obtain the necessary Google Cloud credentials.

## Table of Contents
1. [Initial Setup](#initial-setup)
2. [Obtaining Google Cloud Project ID](#obtaining-google-cloud-project-id)
3. [Authentication Methods](#authentication-methods)
   - [Using Google Cloud SDK](#using-google-cloud-sdk)
   - [Using a Service Account Key](#using-a-service-account-key)
4. [Running the Program](#running-the-program)
5. [Troubleshooting](#troubleshooting)

## Initial Setup

1. Ensure you have Python 3.6 or higher installed on your system:
   ```bash
   python --version
   ```

2. Install the required dependencies:
   ```bash
   pip install google-cloud-datastore>=2.0.0
   ```
   Or using the requirements.txt file:
   ```bash
   pip install -r requirements.txt
   ```

## Obtaining Google Cloud Project ID

Before using the GCDM tool, you need a Google Cloud Project with Datastore/Firestore in Datastore mode enabled:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top of the page
3. Either select an existing project or click "New Project" to create one
4. After selecting/creating a project, note the **Project ID** displayed in the dashboard or in the project dropdown
5. Enable the Datastore API:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Datastore API" or "Firestore API"
   - Click on "Firestore API" (which includes Datastore mode)
   - Click "Enable"

## Authentication Methods

GCDM supports two authentication methods:

### Using Google Cloud SDK

This method is recommended for local development:

1. Install the [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) for your operating system
2. Open a terminal and authenticate:
   ```bash
   gcloud auth application-default login
   ```
3. Follow the browser prompts to sign in with your Google account
4. After successful authentication, credentials are stored locally at:
   - Linux/macOS: `~/.config/gcloud/application_default_credentials.json`
   - Windows: `%APPDATA%\gcloud\application_default_credentials.json`

### Using a Service Account Key

This method is recommended for production or automated environments:

1. In the Google Cloud Console, go to "IAM & Admin" > "Service Accounts"
2. Click "Create Service Account"
3. Enter a name and description for the service account, then click "Create"
4. Assign roles to the service account. At minimum, you need:
   - `Cloud Datastore User` role for basic operations
   - `Cloud Datastore Owner` role for full administrative access
5. Click "Continue" and then "Done"
6. Find your new service account in the list, click the three dots menu, and select "Manage keys"
7. Click "Add Key" > "Create new key"
8. Select "JSON" as the key type and click "Create"
9. The key file will be automatically downloaded to your computer
10. Place the key file in the project directory or a secure location

## Running the Program

After setting up authentication, you can run the program:

```bash
python gcdm.py
```

When prompted, you have two options:
1. Enter your Project ID (if using Google Cloud SDK authentication)
2. Select a service account key file found in your directory

## Troubleshooting

### Authentication Errors

- **Error: Could not automatically determine credentials**
  - Ensure you've completed the authentication steps above
  - Check that your service account has the appropriate roles assigned
  - If using a service account key, verify the file is accessible and not corrupted

- **Error: Permission denied**
  - Verify your service account has the necessary permissions for Datastore
  - Try running with a higher-privileged account

### Project ID Errors

- **Error: Project not found**
  - Double-check your Project ID for typos
  - Ensure the project has Datastore API enabled
  - Verify you have access to the project with the credentials you're using

### API Errors

- **Error: API not enabled**
  - Go to the Google Cloud Console, navigate to "APIs & Services"
  - Enable the Firestore API (which includes Datastore mode)

For further assistance, refer to the [Google Cloud Datastore documentation](https://cloud.google.com/datastore/docs) or create an issue on the project's GitHub repository.
