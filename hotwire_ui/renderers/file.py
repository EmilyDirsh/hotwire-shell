# This file is part of the Hotwire Shell user interface.
#   
# Copyright (C) 2007 Colin Walters <walters@verbum.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import os, stat, signal, datetime, logging, subprocess
from StringIO import StringIO

import gtk, gobject, pango

import hotwire
import hotwire_ui.widgets as hotwidgets
from hotwire.command import Pipeline
from hotwire.fs import FilePath, unix_basename, path_unabs
from hotwire_ui.render import TreeObjectsRenderer, ClassRendererMapping, menuitem
from hotwire.sysdep.fs import Filesystem, File
from hotwire.sysdep.sysenv import SystemEnvironment, GnomeSystemEnvironment
from hotwire.sysdep import is_unix, is_windows
from hotwire.logutil import log_except
from hotwire_ui.pixbufcache import PixbufCache
from hotwire_ui.adaptors.editors import EditorRegistry
from hotwire.util import format_file_size, quote_arg
from hotwire.externals.dispatch import dispatcher
from hotwire.state import Preferences

_logger = logging.getLogger("hotwire.ui.render.File")

class FilePathRenderer(TreeObjectsRenderer):
    def __init__(self, *args, **kwargs):
        if not 'column_types' in kwargs.iterkeys():
            kwargs['column_types'] = [gobject.TYPE_PYOBJECT]
        self.__fs = Filesystem.getInstance()
        self.__basedir = None
        self.__windows_basedir = None
        super(FilePathRenderer, self).__init__(*args,
                                               **kwargs)
        self._table.enable_model_drag_source(gtk.gdk.BUTTON1_MASK,
                                            [('text/uri-list', 0, 0)],
                                            gtk.gdk.ACTION_DEFAULT | gtk.gdk.ACTION_COPY)
        #self._table.enable_model_drag_dest([('text/uri-list', 0, 0)],
        #                                    gtk.gdk.ACTION_DEFAULT | gtk.gdk.ACTION_COPY)        
        self._table.connect("drag-data-get", self.__on_drag_data_get)
        #self._table.connect("drag-data-received", self.__on_drag_data_received)

    def __path_search_equal(self, model, column, key, iter):
        fobj = self._file_for_iter(model, iter)
        if self.__basedir:
            target = path_unabs(fobj.path, self.__basedir)
        else:
            target = fobj.path
        matches = (target.find(key) >= 0)
        # return value intentionally reversed
        return not matches
    
    def __get_column_value(self, obj, column):
        compare_obj = {
            0 : lambda x: x.path.lower(),
            1 : lambda x: x.path.lower(),
            2 : lambda x: x.size,
            3 : lambda x: x.get_mtime(),
            4 : lambda x: x.get_owner(),
            5 : lambda x: x.get_group(),
            6 : lambda x: x.get_permissions_string(),
            7 : lambda x: x.get_mime()
        } [column](obj)
        return compare_obj

    def __standard_compare(self, model, iter1, iter2, user_data):
        ob1 = self._file_for_iter(model, iter1)
        ob2 = self._file_for_iter(model, iter2)

        # fixme: I guess this check shouldn't be necessary here
        if (ob1 == None or ob2 == None):
            return 0
        
        value1 = self.__get_column_value(ob1, user_data)
        value2 = self.__get_column_value(ob2, user_data)
        
        if (self.__folders_before_files):
            if (ob1.is_directory and (not ob2.is_directory)):
                return -1
            if (ob2.is_directory and (not ob1.is_directory)):
                return 1
        
        return cmp(value1, value2)
        
    def _append_column(self, column_type):
        colinfo = self._column_info[column_type]
        colidx = self._table.insert_column_with_data_func(-1, colinfo[0],
                                                            colinfo[2],
                                                            colinfo[1])
        col = self._table.get_column(colidx - 1)
        col.set_sort_column_id(colidx - 1)
        col.set_resizable(True)                

    def _setup_view_columns(self):
        prefs = Preferences.getInstance()
        prefs.monitor_prefs('hotwire.ui.render.File.general.foldersbeforefiles', self.__on_folders_before_files_changed)
        prefs.monitor_prefs('hotwire.ui.render.File.columns.', self.__on_visible_columns_changed)
        self.__folders_before_files = prefs.get_pref('hotwire.ui.render.File.general.foldersbeforefiles', default=True)

        cell_renderer = hotwidgets.CellRendererText(family='Monospace')
        self._column_info = {
            'icon': (_(''), self._render_icon, gtk.CellRendererPixbuf(), 0), 
            'path': (_('Path'), self._render_objtext, hotwidgets.CellRendererText(family='Monospace'), 1), 
            'size': (_('Size'), self._render_size, hotwidgets.CellRendererText(family='Monospace'), 2), 
            'last_modified': (_('Last modified'), self._render_last_modified, hotwidgets.CellRendererText(family='Monospace'), 3), 
            'owner': (_('Owner'), self._render_owner, hotwidgets.CellRendererText(family='Monospace'), 4), 
            'group': (_('Group'), self._render_group, hotwidgets.CellRendererText(family='Monospace'), 5), 
            'permissions': (_('Permissions'), self._render_permissions, hotwidgets.CellRendererText(family='Monospace'), 6), 
            'mime': (_('File type'), self._render_mime, hotwidgets.CellRendererText(family='Monospace'), 7) 
        }

        self._table.set_search_column(0)
        self._table.set_search_equal_func(self.__path_search_equal)

        self._columns = ['icon', 'path', 'size', 'last_modified']
        if self.__fs.supports_owner():
            self._columns.append('owner')
        if self.__fs.supports_group():
            self._columns.append('group')
        self._columns.append('permissions')
        self._columns.append('mime')

        self.__set_sort_funcs()
        self._model.set_default_sort_func(None)
        self._model.set_sort_column_id(1, gtk.SORT_ASCENDING)

        for col in self._columns:
            self._append_column(col)

        self._table.get_column(0).set_spacing(0)
        self._table.get_column(1).set_spacing(0)
        self._linkcolumns.append(self._table.get_column(1))
        self.__sync_visible_columns()

    def _file_for_iter(self, model, iter):
        return model.get_value(iter, 0)

    def _render_icon(self, col, cell, model, iter):
        obj = self._file_for_iter(model, iter)
        icon_name = obj.icon
        if icon_name:
            if icon_name.startswith(os.sep):
                pixbuf = PixbufCache.getInstance().get(icon_name)
                cell.set_property('pixbuf', pixbuf)
            else:
                cell.set_property('icon-name', icon_name)
        else:
            cell.set_property('icon-name', None)

    def _render_objtext(self, col, cell, model, iter):
        obj = self._file_for_iter(model, iter)
        path = obj.path
        if self.__basedir:
            if self.__windows_basedir is not None:
                bdir = self.__windows_basedir
            else:
                bdir = self.__basedir
                
            # Strip leading / unless we're in root
            if len(bdir) > 1:
                offset = 1
            else:
                offset = 0 
            text = path[len(self.__basedir)+offset:]
        else:
            text = path
        cell.set_property('text', text)

    def _render_size(self, col, cell, model, iter):
        obj = self._file_for_iter(model, iter)
        size = obj.get_size()
        if size is not None: 
            cell.set_property('text', format_file_size(size))
        else:
            cell.set_property('text', '')

    def _render_last_modified(self, col, cell, model, iter):
        obj = self._file_for_iter(model, iter)
        mtime = obj.get_mtime()
        if mtime is not None:
            dt = datetime.datetime.fromtimestamp(mtime) 
            cell.set_property('text', dt.isoformat(' '))
        else:
            cell.set_property('text', '')

    def _render_owner(self, col, cell, model, iter):
        obj = self._file_for_iter(model, iter)
        cell.set_property('text', obj.get_owner() or '')

    def _render_group(self, col, cell, model, iter):
        obj = self._file_for_iter(model, iter)
        cell.set_property('text', obj.get_group() or '')
            
    def _render_permissions(self, col, cell, model, iter):
        obj = self._file_for_iter(model, iter)
        perms = obj.get_permissions_string()
        cell.set_property('text', perms or '')
        
    def _render_mime(self, col, cell, model, iter):
        obj = self._file_for_iter(model, iter)
        mime = obj.get_mime()
        cell.set_property('text', mime or '')
        
    @log_except(_logger)
    def __handle_file_change(self, signal=None, sender=None):
        fobj = sender
        _logger.debug("got file change for %r", fobj)
        self._signal_obj_changed(fobj, colidx=0)

    def _get_row(self, obj):
        if isinstance(obj, File):
            fobj = obj
        else:
            fobj = self.__fs.get_file(obj)
        dispatcher.connect(self.__handle_file_change, sender=fobj)
        return (fobj,)
    
    def append_obj(self, obj, **kwargs):
        row = self._get_row(obj)
        if self.__basedir is not False:
            bn,fn = os.path.split(row[0].path)
            if self.__basedir is None:
                _logger.debug("using basedir %s", bn)
                self.__basedir = bn
                # Windows has a more complicated notion of base directory.
                if is_windows():
                    self.__windows_basedir = os.path.splitdrive(self.__basedir)[-1]               
                for row in self._liststore:
                    self._liststore.row_changed(row.path, row.iter)
            elif bn.startswith(self.__basedir):
                pass
            else:
                _logger.debug("basedir %s does not match %s", self.__basedir, bn)                
                self.__basedir = False
                for row in self._liststore:
                    self._liststore.row_changed(row.path, row.iter)                
        self._liststore.append(row)

    def _onclick_iter(self, iter):
        self.__do_open(self._file_for_iter(self._model, iter))
        return True

    def __do_open(self, obj):
        if obj.test_directory(follow_link=True):
            self.context.do_cd(obj.path)
        else:    
            self.__fs.launch_open_file(obj.path, self.context.get_cwd())  
            
    def __on_edit_activated(self, menuitem, cwd, prefeditor, fpath):
        prefeditor.run(cwd, fpath)

    def _get_menuitems(self, iter):
        fobj = self._file_for_iter(self._model, iter)
        items = self.__fs.get_file_menuitems(fobj, context=self.context)
        if items:
            items.append(gtk.SeparatorMenuItem())
        if fobj.is_directory:
            menuitem = gtk.ImageMenuItem(_('Open Folder in New Tab'))
            menuitem.set_property('image', gtk.image_new_from_stock('gtk-new', gtk.ICON_SIZE_MENU))
            menuitem.connect('activate', self.__on_new_tab_activated, fobj.path)
            items.append(menuitem)
            menuitem = gtk.ImageMenuItem(_('Open Folder in New Window'))
            menuitem.set_property('image', gtk.image_new_from_stock('gtk-new', gtk.ICON_SIZE_MENU))            
            menuitem.connect('activate', self.__on_new_window_activated, fobj.path)
            items.append(menuitem)
            sysenv = SystemEnvironment.getInstance()
            if isinstance(sysenv, GnomeSystemEnvironment):
                items.append(gtk.SeparatorMenuItem())
                menuitem = gtk.MenuItem(_('Open with File Manager'))
                menuitem.connect('activate', self.__on_file_manager_activated, ['nautilus', fobj.path])
                items.append(menuitem)
            items.append(gtk.SeparatorMenuItem())
        
        prefeditor = EditorRegistry.getInstance().get_preferred()
        if prefeditor is not None:
            menuitem = gtk.ImageMenuItem(_('Edit with %s') % (prefeditor.name,))
            menuitem.connect('activate', self.__on_edit_activated, self.context.get_cwd(), prefeditor, fobj.path)
            pbcache = PixbufCache.getInstance()
            pixbuf = pbcache.get(prefeditor.icon, size=16, trystock=True, stocksize=gtk.ICON_SIZE_MENU)
            if pixbuf:
                img = gtk.image_new_from_pixbuf(pixbuf)
                menuitem.set_property('image', img)
            items.append(menuitem)
        menuitem = gtk.ImageMenuItem(_('Copy Path to Input'))
        menuitem.set_property('image', gtk.image_new_from_stock('gtk-copy', gtk.ICON_SIZE_MENU))
        menuitem.connect("activate", self.__on_copypath_activated, fobj.path)
        items.append(menuitem)
        return items
       
    def __on_new_tab_activated(self, menu, path):
        _logger.debug("got new tab for %s", path)
        from hotwire_ui.shell import locate_current_window
        hwin = locate_current_window(self._table)
        hwin.new_tab_hotwire(initcwd=path, initcmd='ls')  
        
    def __on_new_window_activated(self, menu, path):
        _logger.debug("got new window for %s", path)
        from hotwire_ui.shell import locate_current_window
        hwin = locate_current_window(self._table)
        hwin.new_win_hotwire(initcwd=path, initcmd='ls')
        
    def __on_file_manager_activated(self, menu, args):
        subprocess.Popen(args)
        
    def __on_copypath_activated(self, menu, path):
        _logger.debug("got copypath for %s", path)
        from hotwire_ui.shell import locate_current_shell
        hw = locate_current_shell(self._table)
        hw.append_text(path)           

    def __on_drag_data_get(self, tv, context, selection, info, timestamp):
        sel = tv.get_selection()
        model, paths = sel.get_selected_rows()
        _logger.debug("got selection %s %s", model, paths)
        obuf = StringIO()
        for path in paths:
            iter = model.get_iter(path)
            fobj = self._file_for_iter(model, iter)
            obuf.write(fobj.path)
            obuf.write('\r\n')
        selection.set('text/uri-list', 8, obuf.getvalue())

    def __on_drag_data_received(self, tv, context, x, y, selection, info, etime):
        model = tv.get_model()
        sel_data = selection.data
        from hotwire_ui.shell import locate_current_shell
        hw = locate_current_shell(self._table)
        hw.do_copy_url_drag_to_dir(sel_data, self.context.get_cwd())

    def __sync_visible_columns(self):
        if (self._table == None):
            return
        prefs = Preferences.getInstance()
        self._table.get_column(self._column_info['size'][3]).set_visible(prefs.get_pref('hotwire.ui.render.File.columns.size', default=True))
        self._table.get_column(self._column_info['last_modified'][3]).set_visible(prefs.get_pref('hotwire.ui.render.File.columns.last_modified', default=True))
        self._table.get_column(self._column_info['owner'][3]).set_visible(prefs.get_pref('hotwire.ui.render.File.columns.owner', default=True))
        self._table.get_column(self._column_info['group'][3]).set_visible(prefs.get_pref('hotwire.ui.render.File.columns.group', default=True))
        self._table.get_column(self._column_info['permissions'][3]).set_visible(prefs.get_pref('hotwire.ui.render.File.columns.permissions', default=True))
        self._table.get_column(self._column_info['mime'][3]).set_visible(prefs.get_pref('hotwire.ui.render.File.columns.mime', default=True))

    def __on_visible_columns_changed(self, prefs, key, value):
        self.__sync_visible_columns()
   
    def __set_sort_funcs(self):
        compare = self.__standard_compare
        column_id = 0
        for col in self._columns:
            self._model.set_sort_func(column_id, compare, self._column_info[col][3])
            column_id = column_id + 1

    def __on_folders_before_files_changed(self, prefs, key, value):
        prefs = Preferences.getInstance()
        self.__folders_before_files = prefs.get_pref('hotwire.ui.render.File.general.foldersbeforefiles', default=True)
        self.__set_sort_funcs()

ClassRendererMapping.getInstance().register(File, FilePathRenderer)
ClassRendererMapping.getInstance().register(FilePath, FilePathRenderer)
