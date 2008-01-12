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

import StringIO

import gobject

from hotwire_ui.render import ClassRendererMapping
from hotwire_ui.renderers.unicode import UnicodeRenderer
from hotwire.cmdalias import AliasRegistry
from hotwire.command import PipelineLanguageRegistry
from hotwire.builtin import BuiltinRegistry
from hotwire.builtins.help import HelpItem
from hotwire.version import __version__

class HelpItemRenderer(UnicodeRenderer):
    def __init__(self, context, **kwargs):
        super(HelpItemRenderer, self).__init__(context, monospace=False, **kwargs)
        self._buf.set_property('text', '')
        
    def __help_all(self):
        self._buf.insert_markup('Hotwire <i>%s</i>\n\n' % (__version__,))
        self._buf.insert_markup(_('New to Hotwire?'))
        self._buf.insert_markup(' ')
        self.append_link(_('View Tutorial'), 'http://hotwire-shell.org/trac/wiki/GettingStarted')
        self._buf.insert_markup('\n\n')

        self._buf.insert_markup('<larger>%s:</larger>\n' % (_('Languages'),))
        languages = list(PipelineLanguageRegistry.getInstance())
        languages.sort(lambda a,b: cmp(a.langname, b.langname))
        for language in languages:
            if not language.prefix:
                continue
            self._buf.insert_markup('  <b>%s</b> - prefix: <tt>%s</tt>\n' \
                                % tuple(map(gobject.markup_escape_text, (language.langname, language.prefix))))
        self._buf.insert_markup('\n')                    

        self._buf.insert_markup('<larger>%s:</larger>\n' % (_('Builtin Commands'),))
        builtins = list(BuiltinRegistry.getInstance())
        builtins.sort(lambda a,b: cmp(a.name, b.name))
        for builtin in builtins:
            self.__append_builtin_base_help(builtin)
            self.__append_builtin_aliases(builtin)
            self.__append_builtin_arghelp(builtin)            
            self.__append_builtin_doc(builtin)
            
        self._buf.insert_markup('\n<larger>%s:</larger>\n' % (_('Aliases'),))
        aliases = list(AliasRegistry.getInstance())
        aliases.sort(lambda a,b: cmp(a.name,b.name))
        for alias in aliases:
            self._buf.insert_markup('  <b>%s</b> - %s\n' % tuple(map(gobject.markup_escape_text, (alias.name, alias.target))))

    def __append_builtin_base_help(self, builtin):
        self._buf.insert_markup('  <b>%s</b> - %s%s: <i>%s</i> %s: <i>%s</i>\n' \
                                % (gobject.markup_escape_text(builtin.name),
                                   _('in'),
                                   builtin.get_input_optional() and ' (opt)' or '',
                                   gobject.markup_escape_text(str(builtin.get_input_type())),
                                   _('out'),
                                   gobject.markup_escape_text(str(builtin.get_output_type()))))
        
    def __append_builtin_aliases(self, builtin):
        if not builtin.aliases:
            return
        self._buf.insert_markup('    Aliases: ')
        names = ['<b>%s</b>' % (gobject.markup_escape_text(x),) for x in builtin.aliases]
        self._buf.insert_markup(', '.join(names))
        self._buf.insert_markup('\n')

    def __append_builtin_doc(self, builtin):
        if builtin.__doc__:
            for line in StringIO.StringIO(builtin.__doc__):
                self._buf.insert_markup('    ' + gobject.markup_escape_text(line))
            self._buf.insert_markup('\n')        
                
    def __append_builtin_arghelp(self, builtin):
        if not builtin.options:
            self._buf.insert_markup('    <i>%s</i>\n' % (_('(No options)'),))
            return
        argstr = '  '.join(map(lambda x: ','.join(x), builtin.options))
        self._buf.insert_markup('    %s: ' % (_('Options'),))
        self._buf.insert_markup('<tt>' + gobject.markup_escape_text(argstr) + '</tt>')
        self._buf.insert_markup('\n')                
        
    def __help_items(self, items):
        builtins = BuiltinRegistry.getInstance()        
        for name in items:
            builtin = builtins[name]
            self.__append_builtin_base_help(builtin)
            self.__append_builtin_aliases(builtin)
            self.__append_builtin_arghelp(builtin)
            self.__append_builtin_doc(builtin)

    def get_status_str(self):
        return ''

    def append_obj(self, o):
        if len(o.items) == 0:
            self.__help_all()
        else:
            self.__help_items(o.items)

    def get_autoscroll(self):
        return False
    
    def supports_input(self):
        return False

ClassRendererMapping.getInstance().register(HelpItem, HelpItemRenderer)
