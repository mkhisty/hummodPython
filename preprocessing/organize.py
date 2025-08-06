import os
import shutil
from pathlib import Path
#Copies everything from hummod into structs/ for easier preproccessing.
def copy_des_files(source_directory, destination_directory):
    source_path = Path(source_directory)
    dest_path = Path(destination_directory)
    
    if not source_path.exists():
        print(f"Error: Source directory '{source_directory}' does not exist.")
        return
    
    dest_path.mkdir(parents=True, exist_ok=True)
    
    # Counter for statistics
    copied_count = 0
    skipped_count = 0
    
    print(f"Searching for .DES files in: {source_path}")
    print(f"Copying to: {dest_path}")
    print("-" * 50)
    
    # Recursively find all .DES files
    for des_file in source_path.rglob("*.DES"):
        try:
            # Get just the filename for the destination
            dest_file = dest_path / des_file.name
            
            # Handle filename conflicts
            if dest_file.exists():
                # Create a unique name by adding the parent directory name
                parent_name = des_file.parent.name
                name_stem = des_file.stem
                name_suffix = des_file.suffix
                
                counter = 1
                while dest_file.exists():
                    if counter == 1:
                        # First try: add parent directory name
                        new_name = f"{name_stem}_{parent_name}{name_suffix}"
                    else:
                        # Subsequent tries: add counter
                        new_name = f"{name_stem}_{parent_name}_{counter}{name_suffix}"
                    
                    dest_file = dest_path / new_name
                    counter += 1
                
                print(f"Name conflict resolved: {des_file.name} -> {dest_file.name}")
            
            # Copy the file
            shutil.copy2(des_file, dest_file)
            print(f"Copied: {des_file.relative_to(source_path)} -> {dest_file.name}")
            copied_count += 1
            
        except Exception as e:
            print(f"Error copying {des_file}: {e}")
            skipped_count += 1
    
    # Print summary
    print("-" * 50)
    print(f"Summary:")
    print(f"  Files copied: {copied_count}")
    print(f"  Files skipped: {skipped_count}")
    print(f"  Destination: {dest_path}")

source_dir = "../hummod"  # Current directory as default

dest_dir = "structs"

# Confirm before proceeding
print(f"\nSource: {os.path.abspath(source_dir)}")
print(f"Destination: {os.path.abspath(dest_dir)}")


c = input("Will copy all .DES and flatten (c to cancel)")

if(c.lower() != "c" ):
    copy_des_files(source_dir, dest_dir)
