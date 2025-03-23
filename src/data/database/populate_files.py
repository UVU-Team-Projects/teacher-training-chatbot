from database import get_db
from crud import create_active_file
import os
from sqlalchemy.exc import IntegrityError

def add_markdown_files():
    """
    Adds all markdown files from the data/markdown_files directory to the active_files table.
    """
    # Define the root directory of your project
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

    # Construct the path to the markdown files
    markdown_files_dir = os.path.join(project_root, "data", "markdown_files")

    print(f"Searching for markdown files in: {markdown_files_dir}")

    # Check if directory exists
    if not os.path.exists(markdown_files_dir):
        print(f"Error: Directory not found: {markdown_files_dir}")
        return

    # Get list of markdown files
    markdown_files = [f for f in os.listdir(markdown_files_dir) if f.endswith('.md')]

    if not markdown_files:
        print("No markdown files found in the directory.")
        return

    print(f"Found {len(markdown_files)} markdown files.")

    # Add each file to the database
    for filename in markdown_files:
        filepath = os.path.join(markdown_files_dir, filename)
        try:
            with open(filepath, "rb") as f:
                file_content = f.read()

            # Try to create the file in the database
            result = create_active_file(name=filename, file_content=file_content)
            if result:
                print(f"Successfully added {filename} to the database.")
            else:
                print(f"Failed to add {filename} to the database.")
        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")

if __name__ == "__main__":
    add_markdown_files() 