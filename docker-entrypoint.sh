#!/bin/bash
set -e

# If command starts with an option, prepend streamlit run
if [ "${1:0:1}" = '-' ]; then
  set -- streamlit run src/web/web.py "$@"
fi

# Initialize the database if setup_database.sh exists
if [ -f "/workspace/setup_database.sh" ]; then
  echo "Setting up database..."
  bash /workspace/setup_database.sh
fi

# Execute the given or default command
exec "$@"