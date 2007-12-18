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

import os,sys,shutil,stat,platform,logging
from cStringIO import StringIO

import gobject

import hotwire
from hotwire.fs import unix_basename, FilePath
from hotwire.async import MiniThreadPool
from hotwire.sysdep import is_windows, is_unix
import hotwire.sysdep.fs_impl

_logger = logging.getLogger("hotwire.sysdep.Filesystem")

class BaseFilesystem(object):
    def __init__(self):
        self.fileklass = File
        self._override_conf_dir = None
        self._trashdir = os.path.expanduser('~/.Trash')
        self.makedirs_p(self._trashdir)

    def get_basename_is_ignored(self, bn):
        return bn.startswith('.')
    
    def get_monitor(self, path, cb):
        raise NotImplementedError()

    def get_file(self, path):
        f = self.fileklass(path)
        f.get_stat()
        return f
    
    def get_file_sync(self, path):
        f = self.fileklass(path)
        f.get_stat_sync()
        return f
        
    def get_file_icon_name(self, file_obj):
        if file_obj.icon:
            return file_obj.icon
        if file_obj.icon_error:
            return None
        icon = self._load_file_icon(file_obj)
        if not icon:
            file_obj.set_icon_error(True)
            return None
        file_obj.set_icon(icon)
        return file_obj.icon
        
    def _load_file_icon(self, fobj):
        if stat.S_ISDIR(fobj.stat.st_mode):
            fobj.icon = 'gtk-directory'
        fobj.icon = 'gtk-file'

    def launch_open_file(self, path, cwd=None):
        raise NotImplementedError()

    def launch_edit_file(self, path):
        raise NotImplementedError()

    def get_file_menuitems(self, file_obj, context=None):
        return []

    def get_conf_dir(self):
        if self._override_conf_dir:
            target = self._override_conf_dir
        else:
            target = self._get_conf_dir_path()
        return self.makedirs_p(target)
    
    def get_system_conf_dir(self):
        if self._override_conf_dir:
            return None
        try:
            syspath = self._get_system_conf_dir_path()
        except NotImplementedError, e:
            return None
        return syspath 
        
    def _get_conf_dir_path(self):
        raise NotImplementedError()

    def _get_system_conf_dir_path(self):
        raise NotImplementedError()
    
    def set_override_conf_dir(self, path):
        self._override_conf_dir = path
    
    def make_conf_subdir(self, *args):
        path = os.path.join(self.get_conf_dir(), *args)
        return self.makedirs_p(path)
    
    def get_path_generator(self):
        raise NotImplementedError()

    def executable_on_path(self, execname):
        for dpath in self.get_path_generator():
            epath = FilePath(execname, dpath)
            try:
                fobj = self.get_file_sync(epath)
            except FileStatError, e:
                continue            
            if fobj.is_executable():
                return epath
        return False

    def path_inexact_executable_match(self, path):
        """This function is a hack for Windows; essentially we
        allow using "python" as an exact match for "python.exe"."""
        return False

    def move_to_trash(self, path):
        bn = unix_basename(path)
        newf = os.path.join(self._trashdir, bn)
        try:
            statbuf = os.stat(newf) 
        except OSError, e:
            statbuf = None
        if statbuf:
            _logger.debug("Removing from trash: %s", newf) 
            if stat.S_ISDIR(statbuf.st_mode):
                shutil.rmtree(newf, onerror=lambda f,p,e:_logger.exception("Failed to delete '%s' from trash", newf))
        shutil.move(path, newf)

    def get_trash_item(self, name):
		return os.path.join(self._trashdir, name)

    def undo_trashed(self, args):
        for arg in args:
            trashed = self.get_trash_item(unix_basename(arg))
            if trashed:
                shutil.move(trashed, arg)

    def makedirs_p(self, path):
        try:
            os.makedirs(path)
        except OSError, e:
            # hopefully it was EEXIST...
            pass
        return path
    
    def supports_owner(self):
        return False
    
    def supports_group(self):
        return False
    
class FileStatError(Exception):
    def __init__(self, cause):
        super(FileStatError, self).__init__()
        self.cause = cause

class File(gobject.GObject):
    __gsignals__ = {
        "changed" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
    }

    def __init__(self, path):
        super(File, self).__init__()
        self.path = path
        self.stat = None
        self.xaccess = None
        self.icon = None
        self.icon_error = False
        self.__permstring = None
        self.target_stat = None
        self.stat_error = None

    def is_directory(self, follow_link=False):
        if not self.stat:
            return False
        if follow_link and stat.S_ISLNK(self.stat.st_mode):
            stbuf = self.target_stat
        else:
            stbuf = self.stat
        return stbuf and stat.S_ISDIR(stbuf.st_mode)
    
    def is_executable(self):
        return self.xaccess

    def get_size(self):
        if self.stat and stat.S_ISREG(self.stat.st_mode):
            return self.stat.st_size
        return None

    def get_mtime(self):
        if self.stat:
            return self.stat.st_mtime
        return None
    
    def get_mode(self):
        return self.stat and self.stat.st_mode
    
    def get_permissions(self):
        return self.stat and self.stat.st_mode
    
    def get_file_type_char(self):
        if self.is_directory():
            return 'd'
        return '-'    

    def get_permissions_string(self):
        if self.__permstring:
            return self.__permstring
        
        perms = self.get_permissions()
        if not perms:
            return
        buf = StringIO()
                
        buf.write(self.get_file_type_char())
        
        if perms & stat.S_ISUID: buf.write('s')
        elif perms &stat.S_IRUSR: buf.write('r')
        else: buf.write('-')
        if perms & stat.S_IWUSR: buf.write('w')
        else: buf.write('-')
        if perms & stat.S_IXUSR: buf.write('x')
        else: buf.write('-')
        
        if perms & stat.S_ISGID: buf.write('s')
        elif perms & stat.S_IRGRP:buf.write('r')
        else: buf.write('-')
        if perms & stat.S_IWGRP: buf.write('w')
        else: buf.write('-')
        if perms & stat.S_IXGRP: buf.write('x')
        else: buf.write('-')
        
        if perms & stat.S_IROTH: buf.write('r')
        else: buf.write('-')
        if perms & stat.S_IWOTH: buf.write('w')
        else: buf.write('-')
        if perms & stat.S_IXOTH: buf.write('x')
        else: buf.write('-')
        
        self.__permstring = buf.getvalue()
        return self.__permstring
    
    def get_mime(self):
        return None

    def get_stat(self):
        self._get_stat_async()

    def _get_stat_async(self):
        MiniThreadPool.getInstance().run(self.__get_stat_signal)
        
    def get_stat_sync(self):
        self._do_get_stat(rethrow=True)
        self._do_get_xaccess()        

    def _do_get_stat(self, rethrow=False):
        try:
            self.stat = hasattr(os, 'lstat') and os.lstat(self.path) or os.stat(self.path)
            if stat.S_ISLNK(self.stat.st_mode):
				try:
					self.target_stat = os.stat(self.path)
				except OSError, e:
					self.target_stat = None		
        except OSError, e:
            _logger.debug("Failed to stat '%s': %s", self.path, e)
            self.stat_error = str(e)
            if rethrow:
                raise FileStatError(e)
            
    def _do_get_xaccess(self):
        self.xaccess = os.access(self.path, os.X_OK)        

    def __get_stat_signal(self):
        self._do_get_stat()
        self._do_get_xaccess()
        gobject.idle_add(lambda: self.emit("changed"), priority=gobject.PRIORITY_LOW)
        
    def set_icon(self, icon):
        self.icon = icon
        
    def set_icon_error(self, err):
        self.icon_error = err

_module = None
if is_unix():
    try:
        import hotwire.sysdep.fs_impl.fs_gnomevfs
        _module = hotwire.sysdep.fs_impl.fs_gnomevfs
    except:
        import hotwire.sysdep.fs_impl.fs_unix
        _module = hotwire.sysdep.fs_impl.fs_unix
elif is_windows():
    import hotwire.sysdep.fs_impl.fs_win32
    _module = hotwire.sysdep.fs_impl.fs_win32
else:
    raise NotImplementedError("No Filesystem implemented for %s!" % (platform.system(),))

_instance = None
class Filesystem(object):
    @staticmethod
    def getInstance():
        global _instance
        if _instance is None:
            _instance = _module.getInstance()
        return _instance
