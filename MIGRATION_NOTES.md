# Migration Notes

## What Changed

The application has been restructured from a single-file Flask app to a proper application structure using the Flask application factory pattern.

## New Structure

- **app/**: Main application package
  - **__init__.py**: Application factory
  - **config.py**: Centralized configuration
  - **routes/**: Route blueprints organized by feature
  - **utils/**: Utility functions (CouchDB, logging)
  - **templates/**: HTML templates
  - **static/**: Static files (CSS, images)

## Old Files (Can be removed)

The following files are no longer needed and can be safely deleted:
- `app.py` (replaced by `app/__init__.py` and `run.py`)
- `csv_mapper_routes.py` (moved to `app/routes/csv_mapper.py`)
- `tombstone_routes.py` (moved to `app/routes/tombstone.py`)

## How to Run

1. Install dependencies: `pip install -r requirements.txt`
2. Run the application: `python run.py`
3. Access at: `http://localhost:8000`

## Configuration

All sensitive credentials are now stored in a `.env` file for security.

1. **Create your `.env` file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with your actual credentials:**
   - `SECRET_KEY`: Flask secret key
   - `COUCHDB_URL`: CouchDB database URL
   - `COUCHDB_USERNAME`: CouchDB username
   - `COUCHDB_PASSWORD`: CouchDB password
   - `ADMIN_USERNAME`: Admin login username
   - `ADMIN_PASSWORD`: Admin login password

**Important:** The `.env` file is gitignored and will never be committed. Always use `.env` for credentials, never hardcode them in the code.

## Performance

- No performance changes - all functionality remains the same
- Code is now better organized and easier to maintain
- No database required (still uses CSV files and sessions)

