import os

folders = ['music', 'rooms', 'images']

def helper(path):
    # if path exists, return path
    if os.path.exists(path):
        return path
    # if path doesn't exist, try to find it in the folders
    for folder in folders:
        new_path = os.path.join(folder, path)
        if os.path.exists(new_path):
            return new_path

    return path

