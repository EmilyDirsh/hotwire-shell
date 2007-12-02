import os, sys, logging, re

import hotwire
import hotwire.fs
from hotwire.fs import FilePath, file_is_valid_utf8

from hotwire.builtin import Builtin, BuiltinRegistry
from hotwire.builtins.fileop import FileOpBuiltin
from hotwire.sysdep.fs import Filesystem

_logger = logging.getLogger("hotwire.builtins.FSearch")

class FileStringMatch(object):
    def __init__(self, path, text, start, end):
        self.path = path
        self.text = text
        self.match_start = start
        self.match_end = end

class FSearchBuiltin(FileOpBuiltin):
    _("""Search directory tree for files matching a regular expression.""")
    def __init__(self):
        super(FSearchBuiltin, self).__init__('fsearch',
                                             output=FileStringMatch,
                                             threaded=True)

    def execute(self, context, regexp, path=None):
        fs = Filesystem.getInstance()
        comp_regexp = re.compile(regexp)
        for (dirpath, subdirs, files) in os.walk(path or context.cwd):
            filtered_dirs = []
            for i,dir in enumerate(subdirs):
                if fs.get_basename_is_ignored(dir):
                    filtered_dirs.append(i)
            for c,i in enumerate(filtered_dirs):
                del subdirs[i-c]
            for f in files:
                if fs.get_basename_is_ignored(f):
                    continue
                fpath = FilePath(f, dirpath)
                if not file_is_valid_utf8(fpath):
                    continue
                fp = None
                try:
                    fp = open(fpath, 'r') 
                    for line in fp:
                        match = comp_regexp.search(line)
                        if match:
                            yield FileStringMatch(fpath, line[:-1], match.start(), match.end())
                    fp.close()
                except OSError, e:
                    _logger.exception(_("Failed searching file"))
BuiltinRegistry.getInstance().register(FSearchBuiltin())
