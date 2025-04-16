import os
import re
import shutil
from datasketch import MinHash, MinHashLSH
from tqdm import tqdm
import time
import multiprocessing

# --- Configuration ---
# Set the base path for relative paths
script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.join(script_dir, os.pardir)
base_dir = os.path.abspath(base_dir)

DATA_DIR = base_dir  # Directory containing the .txt files (relative to script location)
CLEANED_DIR = os.path.join(base_dir, "cleaned_texts")
DUPLICATE_DIR = os.path.join(base_dir, "duplicate_texts")
THRESHOLD = 0.90  # Jaccard similarity threshold for duplicates (90%)
NUM_PERM = 128    # Number of permutations for MinHash
NUM_CORES = multiprocessing.cpu_count() - 4 # Use all available cores - 4

# --- Helper Functions ---

def normalize_text(text):
    """Basic text cleaning: lowercase, remove extra whitespace, normalize line breaks."""
    text = text.lower()
    text = re.sub(r'\s+', ' ', text).strip() # Replace multiple whitespace chars with single space
    text = re.sub(r'(\r\n|\r|\n)', '\n', text) # Normalize line endings to \n
    text = re.sub(r'\n{3,}', '\n\n', text) # Replace 3+ newlines with 2 (paragraph breaks)
    return text

def get_shingles(text, k=5):
    """Convert text into a set of k-shingles."""
    shingles = set()
    text = normalize_text(text) # Normalize before shingling
    if not text:
        return shingles
    for i in range(len(text) - k + 1):
        shingles.add(text[i:i+k])
    return shingles

# --- Worker Function for Parallel Processing ---
def process_file_worker(filepath):
    """Reads, cleans, and computes MinHash for a single file."""
    filename = os.path.basename(filepath)
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        cleaned_content = normalize_text(content)
        if not cleaned_content:
            # print(f"Skipping empty or invalid file: {filename}") # Reduce noise
            return filename, None, "empty or invalid"

        m = MinHash(num_perm=NUM_PERM)
        shingles = get_shingles(cleaned_content)
        if not shingles:
            # print(f"Skipping file (too short after cleaning?): {filename}") # Reduce noise
             return filename, None, "too short after cleaning"
        for s in shingles:
            m.update(s.encode('utf-8'))

        return filename, m, None # Return filename, MinHash object, and no error

    except Exception as e:
        print(f"Error processing file {filename}: {e}")
        return filename, None, str(e) # Return filename, None for MinHash, and error message

# --- Main Script ---

if __name__ == "__main__":
    start_time = time.time()

    # Create output directories if they don't exist
    os.makedirs(CLEANED_DIR, exist_ok=True)
    os.makedirs(DUPLICATE_DIR, exist_ok=True)

    # --- 1. Identify all .txt files ---
    all_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".txt") and os.path.isfile(os.path.join(DATA_DIR, f))]
    print(f"Found {len(all_files)} .txt files in {DATA_DIR}")

    if not all_files:
        print("No .txt files found. Exiting.")
        exit()

    # --- 2. Initialize MinHash LSH ---
    # LSH index helps find potential duplicates quickly without comparing all pairs.
    lsh = MinHashLSH(threshold=THRESHOLD, num_perm=NUM_PERM)

    # --- 3. Process files in parallel: Compute MinHash ---
    minhashes = {}
    files_to_process = [os.path.join(DATA_DIR, f) for f in all_files]
    processed_count = 0
    skipped_files = {} # Store filenames and reasons for skipping

    print(f"Processing {len(files_to_process)} files using {NUM_CORES} cores...")

    # Use multiprocessing Pool
    with multiprocessing.Pool(processes=NUM_CORES) as pool:
        # Use imap_unordered for potentially better performance and progress tracking
        results = tqdm(
            pool.imap_unordered(process_file_worker, files_to_process),
            total=len(files_to_process),
            desc="Hashing Files (Parallel)"
        )

        for filename, m, error_msg in results:
            if m is not None:
                minhashes[filename] = m
                processed_count += 1
            else:
                skipped_files[filename] = error_msg

    print(f"Finished hashing. Successfully processed {processed_count} files.")
    if skipped_files:
        print(f"Skipped {len(skipped_files)} files due to errors or content issues:")
        # for fname, reason in skipped_files.items():
        #     print(f"  - {fname}: {reason}") # Optionally print details

    # --- 4. Populate LSH index (sequentially) ---
    print("Populating LSH index...")
    for filename, m in tqdm(minhashes.items(), desc="Indexing Hashes"):
         lsh.insert(filename, m)


    # --- 5. Identify Duplicates using LSH ---
    processed = set()
    duplicates_found = set() # Files identified as duplicates of another
    # Start unique set only with files that were successfully processed
    unique_files = set(minhashes.keys())

    print("Querying LSH to find near-duplicates...")
    for filename in tqdm(minhashes.keys(), desc="Finding Duplicates"):
        if filename in processed:
            continue

        # Query LSH for potential duplicates
        result = lsh.query(minhashes[filename])

        # The first item in result is always the query item itself
        potential_duplicates = [res for res in result if res != filename]

        # Add the query file to processed set
        processed.add(filename)

        if potential_duplicates:
             # Mark all potential duplicates as processed and add to duplicates_found set
             # Keep the 'filename' (the first one encountered in this group) as the original.
            for dup_filename in potential_duplicates:
                 if dup_filename not in processed:
                    duplicates_found.add(dup_filename)
                    unique_files.discard(dup_filename) # Remove from unique set
                    processed.add(dup_filename) # Mark as processed


    print(f"Identified {len(duplicates_found)} duplicate files.")
    # Ensure unique_files only contains keys present in minhashes before calculation
    actual_unique_count = len(unique_files)
    print(f"Found {actual_unique_count} unique files (among successfully processed).")

    # --- 6. Move Duplicates and Clean/Save Unique Files ---
    print("Moving duplicate files...")
    for filename in tqdm(duplicates_found, desc="Moving Duplicates"):
        source_path = os.path.join(DATA_DIR, filename)
        target_path = os.path.join(DUPLICATE_DIR, filename)
        if os.path.exists(source_path): # Check if it wasn't skipped/missing
            try:
                shutil.move(source_path, target_path)
            except Exception as e:
                print(f"Error moving duplicate file {filename}: {e}")
        else:
            print(f"Warning: Could not move duplicate {filename}, source file not found (was it skipped?).")


    print("Cleaning and saving unique files...")
    # Iterate only over the files deemed unique AFTER LSH processing
    for filename in tqdm(unique_files, desc="Cleaning Unique Files"):
         # We know these filenames exist in minhashes, but double-check source exists
         source_path = os.path.join(DATA_DIR, filename)
         target_path = os.path.join(CLEANED_DIR, filename)

         if not os.path.exists(source_path):
             print(f"Warning: Source file for unique item not found (already moved? skipped?): {filename}")
             continue

         try:
            # Re-read original content for final cleaning
            with open(source_path, 'r', encoding='utf-8', errors='ignore') as f_in:
                 content = f_in.read()

            cleaned_content = normalize_text(content)

            # Write cleaned content to the cleaned directory
            with open(target_path, 'w', encoding='utf-8') as f_out:
                f_out.write(cleaned_content)

            # Remove the original file after successful copy and clean
            os.remove(source_path) # Uncomment this line to DELETE originals instead of just moving duplicates

         except FileNotFoundError:
             print(f"Warning: Original file not found (already moved?): {filename}")
         except Exception as e:
            print(f"Error cleaning/saving file {filename}: {e}")


    end_time = time.time()
    print(f"\n--- Processing Complete ---")
    print(f"Total time: {end_time - start_time:.2f} seconds")
    print(f"Unique files cleaned and saved to: {CLEANED_DIR}")
    print(f"Duplicate files moved to: {DUPLICATE_DIR}")
    if skipped_files:
         print(f"Note: {len(skipped_files)} files were skipped during processing (e.g., empty, too short, errors).")
    # If you uncommented the os.remove line:
    # print(f"Original unique files removed from: {DATA_DIR}")
