# This file is part of the Hotwire Shell project API.

# Copyright (C) 2007 Colin Walters <walters@verbum.org>

# Permission is hereby granted, free of charge, to any person obtaining a copy 
# of this software and associated documentation files (the "Software"), to deal 
# in the Software without restriction, including without limitation the rights 
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies 
# of the Software, and to permit persons to whom the Software is furnished to do so, 
# subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all 
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A 
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE X CONSORTIUM BE 
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, 
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR 
# THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import os, shutil

import hotwire
from hotwire.fs import FilePath, unix_basename
from hotwire.sysdep.fs import Filesystem

from hotwire.builtin import BuiltinRegistry
from hotwire.builtins.fileop import FileOpBuiltin

class RmBuiltin(FileOpBuiltin):
    __doc__ = _("""Move a file to the trash.""")
    def __init__(self):
        super(RmBuiltin, self).__init__('rm', aliases=['delete'],
                                        undoable=True,
                                        hasstatus=True,
                                        threaded=True)

    def execute(self, context, args):
        sources = map(lambda arg: FilePath(arg, context.cwd), args) 
        sources_total = len(sources)
        undo_targets = []
        self._status_notify(context, sources_total, 0)
        fs = Filesystem.getInstance()
        try:
            for i,arg in enumerate(sources):
                fs.move_to_trash(arg)
                undo_targets.append(arg)
                self._status_notify(context,sources_total,i+1)
                self._note_modified_paths(context, sources)
        finally:
            context.push_undo(lambda: fs.undo_trashed(undo_targets))
        return []
BuiltinRegistry.getInstance().register(RmBuiltin())
