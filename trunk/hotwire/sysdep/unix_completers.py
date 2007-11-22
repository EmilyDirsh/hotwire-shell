import os,sys

from hotwire.completion import BaseCompleter, Completion
from hotwire.builtins.sh import ShellCompleters
from hotwire.singletonmixin import Singleton

class RpmDbCompleter(Singleton, BaseCompleter):
    def __init__(self):
        super(RpmDbCompleter, self).__init__()
        self.__db = ['foo', 'bar-devel', 'crack-attack']
    def search(self, text, **kwargs):
        for pkg in self.__db:
            if pkg.startswith(text):
                yield Completion(pkg, 0, len(text), default_icon='gtk-floppy')
def rpm_completion(context, args, i):
    lastarg = args[i].text
    if lastarg.startswith('-q'):
        return RpmDbCompleter.getInstance()
ShellCompleters.getInstance()['rpm'] = rpm_completion 