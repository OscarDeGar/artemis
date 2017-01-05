import sys
from StringIO import StringIO
from contextlib import contextmanager

from artemis.fileman.local_dir import make_file_dir

__author__ = 'peter'
import numpy as np


def deeprint(obj, memo=None):
    """
    Consise - print.

    TODO: Extend this to make a proper deep-print of any object.
    """
    if isinstance(obj, np.ndarray):
        string = '<%s with shape=%s, dtype=%s at %s%s>' % (obj.__class__.__name__, obj.shape, obj.dtype, hex(id(obj)),
            ', value = '+str(obj) if obj.size<8 else ''
            )
    else:
        string = str(obj)
    return string


_ORIGINAL_STDOUT = sys.stdout
_ORIGINAL_STDERR = sys.stderr


class CaptureStdOut(object):
    """
    An logger that both prints to stdout and writes to file.
    """

    def __init__(self, log_file_path = None, print_to_console = True):
        """
        :param log_file_path: The path to save the records, or None if you just want to keep it in memory
        :param print_to_console:
        """
        self._print_to_console = print_to_console
        if log_file_path is not None:
            # self._log_file_path = os.path.join(base_dir, log_file_path.replace('%T', now))
            make_file_dir(log_file_path)
            self.log = open(log_file_path, 'w')
        else:
            self.log = StringIO()
        self._log_file_path = log_file_path
        self.terminal = _ORIGINAL_STDOUT

    def __enter__(self):
        sys.stdout = self
        sys.stderr = self
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = _ORIGINAL_STDOUT
        sys.stderr = _ORIGINAL_STDERR
        self.close()

    def get_log_file_path(self):
        assert self._log_file_path is not None, "You never specified a path when you created this logger, so don't come back and ask for one now"
        return self._log_file_path

    def write(self, message):
        if self._print_to_console:
            self.terminal.write(message)
        self.log.write(message)
        self.log.flush()

    def close(self):
        if self._log_file_path is not None:
            self.log.close()

    def read(self):
        if self._log_file_path is None:
            return self.log.getvalue()
        else:
            with open(self._log_file_path) as f:
                txt = f.read()
            return txt

    def __getattr__(self, item):
        return getattr(self.terminal, item)


class IndentPrint(object):
    """
    Indent all print statements
    """

    def __init__(self, spacing = 4, show_line = False, show_end = False):
        self.indent = '|'+' '*(spacing-1) if show_line else ' '*spacing
        self.show_end = show_end

    def __enter__(self):
        self.old_stdout = sys.stdout
        sys.stdout = self

    def write(self, message):
        if message=='\n':
            new_message = '\n'
        else:
            new_message = self.indent + message.replace('\n', '\n'+self.indent)
        self.old_stdout.write(new_message)
        # self.old_stdout.flush()

    def close(self):
        self.old_stdout.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = self.old_stdout
        if self.show_end:
            print '```'
