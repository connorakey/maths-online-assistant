from pathlib import Path

def delete_all_cache_files():
    """
    Delete all .jpg files in the workspace/cache directory.

    Returns:
        bool: True if all deletions succeeded, False if any deletion failed.
    """
    success = True
    cache_dir = Path("workspace/cache")

    if not cache_dir.exists() or not cache_dir.is_dir():
        print(f"Path {cache_dir} does not exist or is not a directory.")
        return False

    for file_path in cache_dir.iterdir():
        if file_path.is_file() and file_path.suffix.lower() == ".jpg":
            try:
                file_path.unlink()
                print(f"Deleted file: {file_path}")
            except Exception as e:
                print(f"Error deleting file {file_path}: {e}")
                success = False
        else:
            print(f"Skipping file: {file_path}")

    return success


def delete_all_log_files():
    """
    Delete all .log files in the workspace/logs directory.

    Returns:
        bool: True if all deletions succeeded, False if any deletion failed.
    """
    success = True
    logs_dir = Path("workspace/logs")

    if not logs_dir.exists() or not logs_dir.is_dir():
        print(f"Path {logs_dir} does not exist or is not a directory.")
        return False

    for file_path in logs_dir.iterdir():
        if file_path.is_file() and file_path.suffix.lower() == ".log":
            try:
                file_path.unlink()
                print(f"Deleted file: {file_path}")
            except Exception as e:
                print(f"Error deleting file {file_path}: {e}")
                success = False
        else:
            print(f"Skipping file: {file_path}")

    return success

def delete_all_answer_screenshots():
    """
    Delete all .png files in the workspace/screenshots/answers directory.

    Returns:
        bool: True if all deletions succeeded, False if any deletion failed.
    """
    success = True
    answers_dir = Path("workspace/screenshots/answers")

    if not answers_dir.exists() or not answers_dir.is_dir():
        print(f"Path {answers_dir} does not exist or is not a directory.")
        return False

    for file_path in answers_dir.iterdir():
        if file_path.is_file() and file_path.suffix.lower() == ".png":
            try:
                file_path.unlink()
                print(f"Deleted file: {file_path}")
            except Exception as e:
                print(f"Error deleting file {file_path}: {e}")
                success = False
        else:
            print(f"Skipping file: {file_path}")

    return success


def main():
    while True:
        print("------ Deletion of Items in workspace Utility ------")
        print("Options:")
        print("1. Delete all answers screenshots.")
        print("2. Delete all log files.")
        print("3. Delete all files in the cache directory.")
        print("4. Exit Application")

        option = input("Enter your option (1-4): ")
        option = int(option)
    
        match option:
            case 1:
                delete_all_answer_screenshots()
            case 2:
                delete_all_log_files()
            case 3:
                delete_all_cache_files()
            case 4:
                exit()

if __name__ == "__main__":
    main()