from hotwire.builtin import Builtin, BuiltinRegistry

class TermBuiltin(Builtin):
    """Execute a system command in a new terminal."""
    def __init__(self):
        super(TermBuiltin, self).__init__('term', nostatus=True,
                                          parseargs='str')

    def execute(self, context, arg):
        context.hotwire.open_term(context.cwd, context.pipeline, arg)
        return []
        
BuiltinRegistry.getInstance().register(TermBuiltin())