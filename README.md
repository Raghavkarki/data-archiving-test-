# Data Archiving Application

A Flask-based web application for managing and archiving data from CouchDB. This application provides tools for fetching, filtering, and deleting reports, managing tombstone records, and processing CSV files.

## Features

- **Data Archiving Tool**: Fetch and delete reports by contact ID with form filtering
- **Tombstone Archiving Tool**: Manage and fetch tombstone records from CouchDB
- **CSV Mapper**: Process and rearrange CSV/Excel files with predefined column mappings
- **Deletion Logs**: Track all deletion operations with filtering capabilities
- **Authentication**: Simple session-based authentication

## Project Structure

```
data-archiving/
├── app/
│   ├── __init__.py          # Application factory
│   ├── config.py            # Configuration settings
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py          # Authentication routes
│   │   ├── main.py          # Main data archiving routes
│   │   ├── tombstone.py     # Tombstone routes
│   │   └── csv_mapper.py    # CSV mapper routes
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── couchdb.py       # CouchDB helper functions
│   │   └── logging.py        # Logging utilities
│   ├── static/              # Static files (CSS, JS, images)
│   └── templates/           # HTML templates
├── data/                    # Deletion logs storage
├── tombstone_data/          # Tombstone CSV files
├── run.py                   # Application entry point
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## Installation

1. **Clone or navigate to the project directory**

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

The application uses a `.env` file for secure credential storage. 

1. **Copy the example file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` file with your credentials:**
   ```env
   # Flask Configuration
   SECRET_KEY=your-secret-key-change-in-production
   
   # CouchDB Configuration
   COUCHDB_URL=https://chisdhkuh.sambhavpossible.org/medic
   COUCHDB_USERNAME=medic
   COUCHDB_PASSWORD=your-couchdb-password
   
   # Admin Authentication
   ADMIN_USERNAME=admin
   ADMIN_PASSWORD=your-admin-password
   ```

**Important:** The `.env` file is already in `.gitignore` and will not be committed to version control. Never commit your `.env` file with real credentials.

## Running the Application

1. **Start the application**
   ```bash
   python run.py
   ```

2. **Access the application**
   - Open your browser and navigate to: `http://localhost:8000`
   - Default login credentials:
     - Username: `admin`
     - Password: `admin123`

## Usage

### Data Archiving Tool
- Enter contact IDs (comma-separated) to fetch related reports
- Optionally filter by form names
- View, select, and delete reports individually or in bulk
- All deletion operations are logged

### Tombstone Archiving Tool
- Fetch tombstone records by form type or fetch all
- View and manage tombstone reports
- Delete selected tombstone records
- Download fetched tombstone data as CSV

### CSV Mapper
- Upload CSV or Excel files
- Automatically rearrange columns according to predefined mapping
- Download processed files with "_rearranged" suffix

### Deletion Logs
- View all deletion operations
- Filter by success/failure status
- Track contact IDs and document IDs

## Notes

- The application does not use a local database; all data is stored in CSV files
- Session-based authentication is used (no database required)
- CouchDB connection is required for fetching and deleting reports
- All deletion operations are logged to `data/deletion_logs.csv`
- Tombstone data is saved to `tombstone_data/` directory

## Security Considerations

- Change the default `SECRET_KEY` in production
- Update default admin credentials
- Use environment variables for sensitive configuration
- Ensure proper network security for CouchDB connections

## License

This project is for internal use only.

# data-archiving-test-
