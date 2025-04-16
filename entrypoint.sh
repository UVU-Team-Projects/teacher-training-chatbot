#!/bin/sh
set -e # Exit immediately if a command exits with a non-zero status.

MARKER_FILE="/workspace/.db_populated"

# Check if the database has already been populated
if [ ! -f "$MARKER_FILE" ]; then
  echo "Database not populated yet. Running population script..."
  # Assuming the script is run directly, not via run.py based on your selection
  # If run.py is needed, change this line accordingly
  python -m src.data.database.populate_database 
  echo "Database population complete. Creating marker file."
  touch "$MARKER_FILE"
else
  echo "Database already populated. Skipping population script."
fi

echo "Starting main application..."
# Execute the command passed as arguments to the entrypoint (which will be the CMD from Dockerfile)
exec "$@" 