import contextlib
import os


@contextlib.contextmanager
def switchdir(path):
    _oldCWD = os.getcwd()
    os.chdir(os.path.abspath(path))

    try:
        yield
    finally:
        os.chdir(_oldCWD)
