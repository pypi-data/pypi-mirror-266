import pathlib
import shutil
import os
def list_files(source_dir, keyword=None):

  # Check if source directory exists
  if not os.path.exists(source_dir):
    print(f"Error: Source directory '{source_dir}' does not exist.")
    return

  # Loop through files in the source directory
  for filename in os.listdir(source_dir):
    if keyword:
      # Filter based on keyword (lowercase for case-insensitivity)
      if keyword.lower() not in filename.lower():
        continue
    file_size = os.path.getsize(filename)
    print(filename,file_size)

def copy_files(source_dir, destination_dir, keyword=None):
        for root, dirs, files in os.walk(source_dir):
    # Construct the corresponding subdirectory in the destination
            relative_path = os.path.relpath(root, source_dir)
            dest_subdirectory = os.path.join(destination_dir, relative_path)

    # Create the subdirectory in the destination if it doesn't exist
            if not os.path.exists(dest_subdirectory):
                os.makedirs(dest_subdirectory)

            for file in files:
                source_path = os.path.join(root, file)
                file_size = os.path.getsize(source_path)
                destination_path = os.path.join(dest_subdirectory, file)

            # Apply keyword filter if provided
                if keyword and keyword.lower() not in file.lower():
                    continue

                # Copy the file
                try:
                    shutil.copy2(source_path, destination_path)
                    print(f"Copied: '{source_path}' to '{destination_path}' size = {(file_size/1024)/1024}MB")
                except Exception as e:
                    print(f"Error copying file: {e} size = {(file_size/1024)/1024}MB")
def move_files(source_dir, destination_dir, keyword=None):
        for root, dirs, files in os.walk(source_dir):
    # Construct the corresponding subdirectory in the destination
            relative_path = os.path.relpath(root, source_dir)
            dest_subdirectory = os.path.join(destination_dir, relative_path)

    # Create the subdirectory in the destination if it doesn't exist
            if not os.path.exists(dest_subdirectory):
                os.makedirs(dest_subdirectory)

            for file in files:
                source_path = os.path.join(root, file)
                file_size = os.path.getsize(source_path)
                destination_path = os.path.join(dest_subdirectory, file)

            # Apply keyword filter if provided
                if keyword and keyword.lower() not in file.lower():
                    continue

                # Copy the file
                try:
                    shutil.move(source_path, destination_path)
                    print(f"Moved: '{source_path}' to '{destination_path}' size = {(file_size/1024)/1024}MB")
                except Exception as e:
                    print(f"Error moving file: {e} size = {(file_size/1024)/1024}MB")
def greet(name):
    print(f'Hey {name}!')

def get_folder_size(folder_path: str) -> str:
    total_size = 0
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            total_size += os.path.getsize(file_path)
    return ((total_size/1024)/1024)