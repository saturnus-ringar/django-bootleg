import errno
import os


class NotWritableWarning(RuntimeWarning):
    pass


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
