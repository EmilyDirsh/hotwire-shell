import os,sys,subprocess

from hotwire.builtin import Builtin, BuiltinRegistry
from hotwire.singletonmixin import Singleton
from hotwire.completion import BaseCompleter, Completion
from hotwire.sysdep.fs import Filesystem

class OpenSSHKnownHosts(object):
    def __init__(self):
        self.__path = os.path.expanduser('~/.ssh/known_hosts')
        self.__monitor = None
        self.__hostcache = None
        
    def __on_hostchange(self):
        try:
            f = open(self.__path)
        except:
            _logger.debug("failed to open known hosts")
        hosts = []
        for line in f:
            hostip,rest = line.split(' ', 1)
            if hostip.find(',') > 0:
                host = hostip.split(',', 1)[0]
            else:
                host = hostip
            hosts.append(host)
        self.__hostcache = hosts
        
    def get_hosts(self):
        if self.__monitor is None:
            self.__monitor = Filesystem.getInstance().get_monitor(self.__path, self.__on_hostchange)            
        if self.__hostcache is None:
            self.__on_hostchange()
        return self.__hostcache            
        
class OpenSshKnownHostCompleter(Singleton, BaseCompleter):
  def __init__(self):
    super(OpenSshKnownHostCompleter, self).__init__()
    self.__hosts = OpenSSHKnownHosts()    

  def search(self, text, **kwargs):
    for host in self.__hosts.get_hosts():
      if host.startswith(text):
        yield Completion(host, 0, len(text), exact=False, default_icon='gtk-network')
        
class HotSshBuiltin(Builtin):
    _("""Open a connection via SSH.""")
    def __init__(self):
        super(HotSshBuiltin, self).__init__('ssh', nostatus=True,
                                            parseargs='shglob',
                                            threaded=True)

    def get_completer(self, context, args, i):
        return OpenSshKnownHostCompleter.getInstance()

    def execute(self, context, args, options=[]):
        argv = ['hotssh']
        argv.extend(args)
        subprocess.Popen(argv)
        return []
        
BuiltinRegistry.getInstance().register(HotSshBuiltin())
