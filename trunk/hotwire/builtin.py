import os,sys,imp,logging

import hotwire
from hotwire.singletonmixin import Singleton
from hotwire.fs import DirectoryGenerator

_logger = logging.getLogger("hotwire.Builtin")

class ObjectStreamSchema(object):
    def __init__(self, otype, name=None, opt_formats=[]):
        self.otype = otype
        self.name = name
        self.opt_formats = opt_formats

class InputStreamSchema(ObjectStreamSchema):
    def __init__(self, otype, optional=False, **kwargs):
        super(InputStreamSchema, self).__init__(otype, **kwargs)
        self.optional = optional

class OutputStreamSchema(ObjectStreamSchema):
    def __init__(self, otype, merge_default=False, typefunc=None, **kwargs):
        super(OutputStreamSchema, self).__init__(otype, **kwargs)
        self.merge_default = merge_default
        self.typefunc = typefunc

class HotwireBuiltinArg(object):
    def __init__(self, t, optional, completer_class=None):
        self.argtype = t
        self.optional = optional
        self.completer_class = completer_class

def _attr_or_none(o, a):
    return hasattr(o, a) and getattr(o, a) or None

class Builtin(object):
    def __init__(self, name, 
                 input=None,
                 output=None,
                 outputs=[],
                 options=[],
                 aliases=[], 
                 remote_only=False, 
                 nostatus=False,
                 parseargs='ws-parsed',
                 idempotent=False,
                 undoable=False,
                 hasstatus=False,
                 hasmeta=False,
                 threaded=False,
                 locality='local',
                 api_version=0):
        self.input=input
        self.outputs = [isinstance(o, OutputStreamSchema) and o or OutputStreamSchema(o) for o in (output and [output] or outputs)]
        self.options = options
        self.name = name
        self.aliases = aliases 
        self.remote_only = remote_only 
        self.nostatus = nostatus
        if not parseargs in ('ws-parsed', 'str', 'shglob', 'str-shquoted'):
            raise ValueError('Bad parseargs: %s' % (parseargs,))        
        self.parseargs = parseargs
        self.idempotent = idempotent
        self.undoable = undoable
        self.hasstatus = hasstatus
        self.hasmeta = hasstatus or hasmeta
        self.threaded = threaded
        self.locality = locality
        self.api_version = api_version

    def get_completer(self, *args, **kwargs):
        return None

    def cancel(self, context):
        pass

    def execute(self, context, *args):
        raise NotImplementedError()
    
    def cleanup(self, context):
        pass

    def __get_exec_attr_or_none(self, attr):
        func = self.execute 
        return _attr_or_none(func, attr)

    def get_input(self):
        return self.input

    def get_outputs(self):
        return self.outputs

    def get_input_opt_formats(self):
        if self.input:
            return self.input.opt_formats
        return []
    
    def get_output_opt_formats(self):
        if self.outputs:
            return self.outputs[0].opt_formats
        return []

    def get_aux_outputs(self):
        return self.outputs[1:]

    def get_input_type(self):
        if self.input:
            return self.input.otype
        return None

    def get_input_optional(self):
        if self.input:
            return self.input.optional
        return False

    def get_output_type(self):
        if self.outputs:
            return self.outputs[0].otype
        return None

    def get_output_typefunc(self):
        if self.outputs:
            return self.outputs[0].typefunc
        return None

    def get_locality(self):
        return self.locality

    def get_parseargs(self):
        return self.parseargs or 'ws-parsed'

    def get_options(self):
        return self.options

    def get_idempotent(self):
        return self.idempotent

    def get_undoable(self):
        return self.undoable
    
    def get_threaded(self):
        return self.threaded

    def get_hasstatus(self):
        return self.hasstatus
    
    def get_hasmeta(self):
        return self.hasmeta
    
    def get_api_version(self):
        return self.api_version

class BuiltinRegistry(Singleton):
    def __init__(self):
        self.__builtins = set()

    def __getitem__(self, name):
        for x in self.__builtins:
            if x.name == name or name in x.aliases:
                return x
        raise KeyError(name)

    def __iter__(self):
        for x in self.__builtins:
            yield x

    def register(self, builtin):
        self.__builtins.add(builtin)

import hotwire.builtins.cat
import hotwire.builtins.cd
import hotwire.builtins.cp
import hotwire.builtins.current
import hotwire.builtins.edit
import hotwire.builtins.filter
import hotwire.builtins.fsearch
import hotwire.builtins.help
import hotwire.builtins.history
import hotwire.builtins.ls
import hotwire.builtins.mv
import hotwire.builtins.open
import hotwire.builtins.prop
import hotwire.builtins.proc
import hotwire.builtins.rm
import hotwire.builtins.sh
import hotwire.builtins.term
