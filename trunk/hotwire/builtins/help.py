from hotwire.builtin import Builtin, BuiltinRegistry
from hotwire.completion import BuiltinCompleter

class HelpItem(object):
    def __init__(self, items):
        self.items = items

class HelpBuiltin(Builtin):
    _("""Display help.""")
    def __init__(self):
        super(HelpBuiltin, self).__init__('help',
                                          output=HelpItem,
                                          parseargs='shglob',
                                          idempotent=True)

    def get_completer(self, context, args, i):
        return BuiltinCompleter.getInstance()

    def execute(self, context, args):    
        yield HelpItem(args)
            
    
BuiltinRegistry.getInstance().register(HelpBuiltin())
