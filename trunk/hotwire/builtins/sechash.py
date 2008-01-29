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

import os,sys,md5,sha

import hotwire
from hotwire.builtin import Builtin, BuiltinRegistry, InputStreamSchema
from hotwire.fs import FilePath
from hotwire.sysdep.fs import Filesystem

class SecHashBuiltin(Builtin):
    __doc__ = _("""Create a secure hash (default SHA1) from objects or file arguments.""")
    def __init__(self):
        super(SecHashBuiltin, self).__init__('sechash', '5dbbea87-dc0f-4d37-99d0-af6544aeba72', 
                                             idempotent=True,
                                             input=InputStreamSchema('any', optional=True),
                                             output=str,                                           
                                             options=[['-5', '--md5'],],
                                             threaded=True)

    def execute(self, context, args, options=[]):
        alg = ('-5' in options) and md5 or sha  
        fs = Filesystem.getInstance()
        if (not args) and context.input:
            for val in context.input:
                valstr = str(val)
                hashval = alg.new()
                hashval.update(valstr)
                yield hashval.hexdigest()
        for arg in args:
            fpath = FilePath(arg, context.cwd)
            stream = open(fpath)
            hashval = alg.new()
            buf = stream.read(4096)
            while buf:
                hashval.update(buf)
                buf = stream.read(4096)
            stream.close()
            yield hashval.hexdigest()

BuiltinRegistry.getInstance().register(SecHashBuiltin())
