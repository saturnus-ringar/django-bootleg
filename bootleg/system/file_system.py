import errno
import os
from datetime import datetime
from django.conf import settings


class NotWritableWarning(RuntimeWarning):
    pass


def get_last_dir(path):
    return os.path.basename(os.path.normpath(path))


def get_full_path(filename):
    return os.path.join(settings.BASE_DIR, filename)


def is_writable(directory):
    if os.access(directory, os.W_OK):
        return True

    return False


def mkdir_p(path):
    """http://stackoverflow.com/a/600612/190597 (tzot)"""
    try:
        os.makedirs(path, exist_ok=True)  # Python>3.2
    except TypeError:
        try:
            os.makedirs(path)
        except OSError as exc: # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise


def get_last_modified_file(dir, exclude_pycache=True):
    last_modified = 0
    last_modified_file = None
    for subdir, dirs, files in os.walk(dir):
        for file in files:
            skip = False
            if exclude_pycache and file.endswith(".pyc"):
                skip = True

            if not skip:
                path = os.path.join(subdir, file)
                mtime = os.path.getmtime(path)
                if mtime > last_modified or not last_modified_file:
                    last_modified_file = {}
                    last_modified_file["path"] = path
                    last_modified_file["mtime"] = mtime
                    last_modified_file["date"] = datetime.fromtimestamp(mtime)
                    last_modified = mtime

    return last_modified_file


def write_file(filename, content):
    f = open(filename, "w")
    f.write(content)
    f.close()
