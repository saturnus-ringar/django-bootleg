import os
from os import path


def get_files_recursively(dir, files_to_skip=[]):
    if not path.exists(dir):
        raise OSError("Dir: %s doesn't exist." % dir)
    ret_files = []
    for subdir, dirs, files in os.walk(dir):
        for file in sorted(files):
            if file not in files_to_skip:
                ret_files.append(os.path.join(subdir, file))

    return ret_files
