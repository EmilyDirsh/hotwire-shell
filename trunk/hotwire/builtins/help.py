from hotwire.builtin import Builtin, BuiltinRegistry, OutputStreamSchema

class HelpItem(object):
    pass

class HelpBuiltin(Builtin):
    """Display help."""
    def __init__(self):
        super(HelpBuiltin, self).__init__('help',
                                          output=OutputStreamSchema(HelpItem),
                                          idempotent=True)

    def execute(self, context):
        yield HelpItem()
    
BuiltinRegistry.getInstance().register(HelpBuiltin())