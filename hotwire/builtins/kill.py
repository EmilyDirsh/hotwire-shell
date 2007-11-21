import os,sys,signal

import hotwire

from hotwire.sysdep.proc import ProcessManager, Process
from hotwire.builtin import Builtin, BuiltinRegistry
from hotwire.singletonmixin import Singleton
from hotwire.completion import BaseCompleter, Completion

_signals = []
for sym in dir(signal):
    if sym.startswith('SIG') and sym != 'SIG_DFL' and sym != 'SIG_IGN':
        _signals.append((sym, getattr(signal, sym)))
# This is kind of wasteful, but eh.  Death before inconvenience and all that.
_sigsym_to_value = {}
_sigvalue_to_sym = {}
for sym,num in _signals:
    _sigsym_to_value[sym] = num
    _sigvalue_to_sym[num] = sym

class ProcessCompleter(Singleton, BaseCompleter):
    def __init__(self):
        super(ProcessCompleter, self).__init__() 

    def search(self, text, **kwargs):
        proclist = ProcessManager.getInstance().get_cached_processes()         
        try:
            textint = int(text)
        except ValueError, e:
            textint = None   
        if textint is not None:
            for proc in proclist:
                pidstr = str(proc.pid)
                if pidstr.startswith(text):
                    #try:
                    #    cmd,args = proc.cmd.split(' ')
                    #except ValueError, e:
                    #    cmd = proc.cmd
                    #    args = []
                    #if len(cmd) > 40:
                    #    context_str = '...' + cmd[-37:]
                    #else:
                    #    context_str = cmd[-40:]
                    #pidstr_context = pidstr + ' ' + context_str
                    yield Completion(pidstr, 0, len(text), exact=False, default_icon='gtk-execute')
        else:
            for proc in proclist:
                idx = proc.cmd.find(text)
                if idx >= 0:
                    yield Completion(proc.cmd, idx, len(text), exact=False, default_icon='gtk-execute')

class KillBuiltin(Builtin):
    """Send a signal to a process."""
    def __init__(self):
        options = []
        for num in sorted(_sigvalue_to_sym):
            options.append(['-' + str(num)])
            options.append(['-' + _sigvalue_to_sym[num][3:]])
        super(KillBuiltin, self).__init__('kill',
                                          nostatus=True,
                                          options=options,
                                          parseargs='shglob',                                        
                                          threaded=True)
        
    def get_completer(self, argpos, context):
        return ProcessCompleter.getInstance()        

    def execute(self, context, args, options=[]):
        signum = signal.SIGTERM
        for opt in options:
            optval = opt[1:]
            if optval in _sigsym_to_value:
                signum = _sigsym_to_value['SIG' + optval]
                break
            else:
                try:
                    optnum = int(opt[1:])
                except ValueError, e:
                    continue
                if optnum in _sigvalue_to_sym:
                    signum = optnum
                    break
        argpids = map(int, args)
        for arg in argpids:
            os.kill(arg, signum)
        return []
        
BuiltinRegistry.getInstance().register(KillBuiltin())
