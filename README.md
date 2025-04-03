# Google Cloud Datastore Manager (GCDM)

A command-line interface tool for efficiently managing Google Cloud Datastore entities, kinds, and namespaces. GCDM provides an intuitive text-based interface for viewing, importing, exporting, and deleting datastore data.

## Features

- **Namespace Management**: View, create, and delete namespaces
- **Kind Management**: View, import, export, and remove kinds within a namespace
- **CSV Import/Export**: Easily move data between Datastore and CSV files
- **Smart Filtering**: Search across namespaces, kinds, and CSV files
- **Terminal-Friendly UI**: Clean interface that works in any terminal environment

## Requirements

- Python 3.6+
- Google Cloud account with Datastore/Firestore in Datastore mode enabled
- Google Cloud SDK (for local credential setup) or a service account JSON key file

### Python Dependencies

```
google-cloud-datastore>=2.0.0
```

## Installation

### Setting Up on a Local Machine

1. Clone this repository or download the files:

```bash
git clone <https://github.com/Ang3110/GCloud-Datastore-Manager>
cd gcdm
```

2. Create a virtual environment and install dependencies:

```bash
# Install venv if needed (Ubuntu/Debian)
sudo apt-get install python3-venv  # For Ubuntu/Debian

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Linux/macOS
# OR
venv\Scripts\activate     # On Windows

# Install dependencies
pip install -r requirements.txt
```

3. Set up authentication (choose one method):
   
   a. Using Google Cloud SDK:
   ```bash
   gcloud auth application-default login
   ```
   
   b. Using a service account key:
   ```bash
   # Place your .json key file in the project directory
   # The GCDM tool will locate it automatically
   ```

4. Run the tool:

```bash
python gcdm.py
```

### Setting Up in Google Cloud Shell

1. Open Google Cloud Shell for your project
2. Clone this repository:

```bash
git clone <https://github.com/Ang3110/GCloud-Datastore-Manager>
cd gcdm
```

3. Install dependencies:

```bash
pip install --user -r requirements.txt
```

4. Run the tool (authentication is handled automatically in Cloud Shell):

```bash
python3 gcdm.py
```

### Setting Up on GitHub Codespaces

1. Create a new Codespace from your repository
2. Open a terminal and install dependencies:

```bash
pip install -r requirements.txt
```

3. Upload your service account key file to the Codespace or set up Google Cloud authentication
4. Run the tool:

```bash
python gcdm.py
```

## Usage Guide

### Getting Started

1. Launch the application by running `python gcdm.py`
2. Choose authentication method:
   - Option 1: Enter your GCP Project ID (uses Application Default Credentials)
   - Option 2: Find available default key credential JSON files

3. Once authenticated, you'll enter the namespace selection menu
4. Select a namespace to perform operations on, or create a new one

### Command Reference

- **Numbers**: Select an item from a list
- **ALL**: Select all items in a list
- **NEW \<name>**: Create a new namespace or kind
- **RM**: Remove one or multiple items (using comma/range notation, e.g., 1,3-5)
- **SEARCH \<keywords>**: Filter lists by keywords
- **DOCUMENT**: View developer documentation (available in namespace list)
- **CAB**: Reset filter or return to previous menu
- **ABOUT**: Show information about the tool
- **Ctrl+C**: Exit the application at any time

### Navigation Flow

1. Main Menu → Authentication
2. Authentication → Namespace List
3. Namespace List → Namespace Menu
4. Namespace Menu → Export/Import/Remove Operations

### Common Operations

**Exporting data to CSV:**
1. Select a namespace
2. Choose "Export selected kinds to CSV"
3. Select the kinds to export
4. Specify filenames for the CSV files

**Importing CSV to Datastore:**
1. Select a namespace
2. Choose "Import CSV into this namespace"
3. Select import folder (import or export)
4. Select CSV files to import
5. Choose an existing kind or create a new one

**Removing kinds:**
1. Select a namespace
2. Choose "Remove one or multiple datastore kinds"
3. Select kinds to remove
4. Confirm deletion

## Creating a Requirements File

If the requirements.txt file doesn't exist, create one with:

```bash
echo "google-cloud-datastore>=2.0.0" > requirements.txt
```

## License and Credits

Created by Angello. Feel free to use and modify as needed.

### Educational Purpose

This project was created as an educational learning experience to understand Google Cloud Datastore operations and terminal-based user interfaces in Python.

### Acknowledgments

- **Python.org**: For the excellent documentation on standard libraries that made this project possible
- **Google Cloud Documentation**: For reference on Datastore operations and best practices

For questions, feedback, or collaboration, feel free to create an issue on my github.
