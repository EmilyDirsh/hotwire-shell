from hotwire.builtin import Builtin, BuiltinRegistry, OutputStreamSchema

class LastBuiltin(Builtin):
    """Returns objects generated by previously executed command."""
    def __init__(self):
        super(LastBuiltin, self).__init__('last',
                                          output=OutputStreamSchema('any', 
                                                                    typefunc=lambda hotwire: hotwire.get_last_output()[0]))

    def execute(self, context):
        for obj in context.last_output[1]:
            yield obj
    
BuiltinRegistry.getInstance().register(LastBuiltin())