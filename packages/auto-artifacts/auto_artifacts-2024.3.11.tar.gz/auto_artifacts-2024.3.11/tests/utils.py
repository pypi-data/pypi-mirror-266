import os
import shutil
import hashlib

def sha256(input_integer):
    input_bytes = input_integer.to_bytes((input_integer.bit_length() + 7) // 8, byteorder='big')
    hash_object = hashlib.sha256()
    hash_object.update(input_bytes)
    hex_dig = hash_object.hexdigest()
    return hex_dig

def clear_directory_contents(dir_path):
    # Check if the directory exists
    if not os.path.exists(dir_path):
        print("Directory does not exist:", dir_path)
        return

    # Loop over each entry in the directory
    for entry_name in os.listdir(dir_path):
        # Create full path to the entry
        entry_path = os.path.join(dir_path, entry_name)
        try:
            # Check if it's a file or directory
            if os.path.isfile(entry_path) or os.path.islink(entry_path):
                os.remove(entry_path)  # Remove files and links
            elif os.path.isdir(entry_path):
                shutil.rmtree(entry_path)  # Remove directories
        except Exception as e:
            print(f"Failed to delete {entry_path}. Reason: {e}")