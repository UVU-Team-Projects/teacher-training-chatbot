from crud import *

def main():
    """
    Main function to populate all database tables.
    This script should be run after the database has been initialized.
    """
    print("Starting database population...")
    
    # First, initialize the database
    print("\nInitializing database...")
    if not initialize_database():
        print("Failed to initialize database. Exiting.")
        return
    print(clear_all_tables())
    print_table_contents("student_profiles")
    
    # Then populate all tables using the combined function
    print("\nPopulating all tables...")
    success = populate_all_tables()
    
    if success:
        print("\nAll tables populated successfully!")
    else:
        print("\nSome tables may not have been populated correctly.")

if __name__ == "__main__":
    main() 