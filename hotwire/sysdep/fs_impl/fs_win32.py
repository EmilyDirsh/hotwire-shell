import os,sys,subprocess

import gtk

from hotwire.fs import path_normalize
from hotwire.sysdep.fs import BaseFilesystem
from hotwire.sysdep.win32 import win_exec_re

# TODO - implement native "Recycle Bin" trash functionality.
# involves lots of hackery with shellapi
class Win32Filesystem(BaseFilesystem):
    def __init__(self):
        super(Win32Filesystem, self).__init__()
            
    def _get_conf_dir_path(self):
        return os.path.expanduser('~/Application Data/hotwire')

    def get_path_generator(self):
        for d in os.environ['PATH'].split(';'):
            yield path_normalize(d)

    def get_executable_filter(self):
        return lambda path, stbuf=None: os.access(path, os.X_OK) and win_exec_re.search(path) 

    def path_inexact_executable_match(self, path):
        return win_exec_re.search(path)

def getInstance():
    return Win32Filesystem()