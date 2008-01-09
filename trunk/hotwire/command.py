# This file is part of the Hotwire Shell project API.

# Copyright (C) 2007 Colin Walters <walters@verbum.org>

# Permission is hereby granted, free of charge, to any person obtaining a copy 
# of this software and associated documentation files (the "Software"), to deal 
# in the Software without restriction, including without limitation the rights 
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies 
# of the Software, and to permit persons to whom the Software is furnished to do so, 
# subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all 
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A 
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE X CONSORTIUM BE 
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, 
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR 
# THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import os, sys, threading, Queue, logging, string, re, time, traceback
import posixpath
from StringIO import StringIO

import gobject

import hotwire.fs
from hotwire.fs import path_normalize, FilePath
from hotwire.async import IterableQueue, MiniThreadPool
from hotwire.builtin import BuiltinRegistry, Builtin
import hotwire.util
from hotwire.util import quote_arg, assert_strings_equal
import hotwire.script
import hotwire.externals.shlex as shlex

_logger = logging.getLogger("hotwire.Command")

class HotwireContext(gobject.GObject):
    __gsignals__ = {
        "cwd" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_STRING,)),
    }
    """The interface to manipulating a Hotwire execution shell.  Item
    such as the current working diretory may be changed via this class,
    and subclasses define further extended commands."""
    def __init__(self, initcwd=None):
        super(HotwireContext, self).__init__()
        self.chdir(initcwd or os.path.expanduser('~'))
        _logger.debug("Context created, dir=%s" % (self.get_cwd(),))

    def chdir(self, dir):
        dir = os.path.expanduser(dir)
        newcwd = os.path.isabs(dir) and dir or posixpath.join(self.__cwd, dir)
        newcwd = path_normalize(newcwd)
        _logger.debug("chdir: %s    post-normalize: %s", dir, newcwd)
        os.stat(newcwd) # lose on nonexistent
        self.__cwd = newcwd
        self.emit("cwd", newcwd)
        return self.__cwd

    def get_cwd(self):
        return self.__cwd
    
    def get_gtk_event_time(self):
        return 0

    def info_msg(self, msg):
        _logger.info("msg: %s", msg)

    def get_current_output_type(self):
        return None
    
    def get_current_output(self):
        return None
    
    def get_current_selected_output(self):
        return None

class CommandContext(object):
    """An execution snapshot for a Command.  Holds the working directory
    when the command started, the input stream, and allows accessing
    the execution context."""
    def __init__(self, hotwire):
        self.input = None
        self.input_type = None
        self.input_is_first = False
        self.pipeline = None
        self.cwd = hotwire.get_cwd()
        self.gtk_event_time = hotwire.get_gtk_event_time()
        # This is kind of a hack; we need to store a snapshot of the
        # currently displayed output when executing a new command.
        # We should be sure this isn't creating circular references.
        self.current_output_type = hotwire.get_current_output_type()
        self.current_output = hotwire.get_current_output()
        self.selected_output = hotwire.get_current_selected_output()
        self.hotwire = hotwire
        self.__auxstreams = {}
        self.__metadata_handler = None
        # Private attributes to be used by the builtin
        self.attribs = {}
        self.cancelled = False

    def set_pipeline(self, pipeline):
        self.pipeline = pipeline

    def attach_auxstream(self, auxstream):
        self.__auxstreams[auxstream.name] = auxstream

    def auxstream_append(self, name, obj):
        self.__auxstreams[name].queue.put(obj)

    def auxstream_complete(self, name):
        self.auxstream_append(name, None)

    def get_auxstreams(self):
        for obj in self.__auxstreams.itervalues():
            yield obj

    def push_undo(self, fn):
        self.pipeline.push_undo(fn)

    def set_metadata_handler(self, fn):
        self.__metadata_handler = fn

    def status_notify(self, status, progress=-1):
        self.metadata('hotwire.status', 0, (status, progress))
            
    def metadata(self, metatype, flags, value):
        if self.__metadata_handler:
            self.__metadata_handler(metatype, flags, value)

class CommandQueue(IterableQueue):
    def __init__(self):
        IterableQueue.__init__(self)
        self.opt_type = None

    def negotiate(self, out_fmts, in_fmts):
        _logger.debug("negotating out_fmts: %s in_fmts: %s", out_fmts, in_fmts)
        for fmt in out_fmts:
            if fmt in in_fmts:
                self.opt_type = fmt
                _logger.debug("Negotiated optimized type %s", fmt)
                break
            
    def cancel(self):
        self.put(None)
        
class CommandFileQueue(object):
    """Implements command queue protocol, yielding lines from a file."""
    def __init__(self, f):
        self.__f = f
        
    def negotiate(self, out_fmts, in_fmts):
        pass
        
    def __iter__(self):
        for line in self.__f:
            yield line[:-1]
        self.__f.close()
        self.__f = None
        
    def cancel(self):
        if self.__f is None:
            return
        self.__f.close()
        self.__f = None

class CommandAuxStream(object):
    def __init__(self, command, schema):
        self.command = command
        self.name = schema.name
        self.schema = schema
        self.queue = CommandQueue()

class CommandException(Exception):
    pass

class CommandArgument(str):
    """An argument for a command, with the additional metadata of quotation status."""
    def __new__(cls, value, quoted=False):
        inst = super(CommandArgument, cls).__new__(cls, value)
        inst.isquoted = quoted
        return inst

class Command(gobject.GObject):
    """Represents a complete executable object in a pipeline."""

    __gsignals__ = {
        "complete" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, []),                    
        "metadata" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, gobject.TYPE_STRING, gobject.TYPE_PYOBJECT)),
        "exception" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
    }

    def __init__(self, builtin, args, options, hotwire, tokens=None, in_redir=None, out_redir=None, 
                  out_append=False):
        super(Command, self).__init__()
        self.builtin = builtin
        self.context = CommandContext(hotwire) 
        for schema in self.builtin.get_aux_outputs():
            self.context.attach_auxstream(CommandAuxStream(self, schema))
        if self.builtin.get_hasmeta():
            self.context.set_metadata_handler(lambda *args: self.emit("metadata", *args))
        self.input = None
        self.output = CommandQueue()
        self.map_fn = lambda x: x
        self.args = args
        self.options = options
        self.in_redir = in_redir and FilePath(os.path.expanduser(in_redir), self.context.cwd)
        self.out_redir = out_redir and FilePath(os.path.expanduser(out_redir), self.context.cwd)
        self.out_append = out_append
        
        self.__executing_sync = None
        self._cancelled = False
        self.__tokens = tokens

    def set_pipeline(self, pipeline):
        self.context.set_pipeline(pipeline)

    def set_input(self, input, is_first=False):
        self.input = input       
        self.context.input = self.input
        self.context.input_is_first = is_first
        
    def set_input_type(self, in_type):
        """Note the pipeline object type used for input."""
        self.context.input_type = in_type
        
    def disconnect(self):
        self.context = None
        
    def cancel(self):
        if self._cancelled:
            return
        self._cancelled = True
        self.context.cancelled = True
        if self.context.input:
            self.context.input.cancel()
        self.builtin.cancel(self.context)

    def get_input_opt_formats(self):
        return self.builtin.get_input_opt_formats()

    def get_output_opt_formats(self):
        return self.builtin.get_output_opt_formats()

    def execute(self, force_sync, **kwargs):
        if force_sync or not self.builtin.get_threaded():
            _logger.debug("executing sync: %s", self)
            self.__executing_sync = True
            self.__run(**kwargs)
        else:         
            _logger.debug("executing async: %s", self)              
            self.__executing_sync = False             
            MiniThreadPool.getInstance().run(lambda: self.__run(**kwargs))

    def set_output_queue(self, queue, map_fn):
        self.output = queue
        self.map_fn = map_fn

    def get_auxstreams(self):
        for obj in self.context.get_auxstreams():
            yield obj
    
    def get_tokens(self):
        return self.__tokens

    def __run(self):
        if self._cancelled:
            _logger.debug("%s cancelled, returning", self)
            self.output.put(self.map_fn(None))
            return
        try:
            options = self.options
            matched_files = []
            oldlen = 0
            for globarg_in in self.args:
                if isinstance(globarg_in, CommandArgument) and globarg_in.isquoted:
                    globarg = globarg_in
                    newlen = oldlen                    
                else:
                    globarg = os.path.expanduser(globarg_in)
                    matched_files.extend(hotwire.fs.dirglob(self.context.cwd, globarg))
                    _logger.debug("glob on %s matched is: %s", globarg_in, matched_files) 
                    newlen = len(matched_files)
                if oldlen == newlen:
                    matched_files.append(globarg)
                    newlen += 1
                oldlen = newlen    
            target_args = [matched_files]
            _logger.info("Execute '%s' args: %s options: %s", self.builtin, target_args, options)
            kwargs = {}
            if options:
                kwargs['options'] = options
            if self.output.opt_type and not self.out_redir:
                kwargs['out_opt_format'] = self.output.opt_type
            if self.in_redir:
                _logger.debug("input redirected, opening %s", self.in_redir)
                self.context.input = CommandFileQueue(open(self.in_redir, 'r'))
            if self.out_redir:
                _logger.debug("output redirected, opening %s", self.out_redir)
                outfile = open(self.out_redir, self.out_append and 'a+' or 'w')
            else:
                outfile = None
            try:
                for result in self.builtin.execute(self.context, *target_args, **kwargs):
                    # if it has status, let it do its own cleanup
                    if self._cancelled and not self.builtin.get_hasstatus():
                        _logger.debug("%s cancelled, returning", self)
                        self.output.put(self.map_fn(None))
                        self.emit("complete")                        
                        return
                    if outfile and (result is not None):
                        if isinstance(result, basestring):
                            outfile.write(result)
                        else:
                            outfile.write(repr(result))
                        outfile.write('\n')
                    else:                        
                        self.output.put(self.map_fn(result))
            finally:
                if outfile:
                    outfile.close()
                self.builtin.cleanup(self.context)
        except Exception, e:
            _logger.exception("Caught exception: %s", e)
            self.emit("exception", e)
        self.output.put(self.map_fn(None))
        self.emit("complete")  
        
    def get_executing_sync(self):
        return self.__executing_sync      

    def __str__(self):
        def unijoin(args):
            return ' '.join(map(unicode, args))
        args = [self.builtin.name]
        args.extend(self.options)
        args.extend(map(quote_arg, self.args))
        if self.in_redir:
            args.extend(['<', self.in_redir])
        if self.out_redir:
            args.extend(['>', self.out_redir])            
        return unijoin(args)

class PipelineParseException(Exception):
    pass

class ParsedToken(object):
    def __init__(self, text, start, end=None, was_unquoted=False, quoted=False):
        self.text = text 
        self.start = start
        self.end = end or (start + len(text))
        self.was_unquoted = was_unquoted
        self.quoted = quoted

    def __repr__(self):
        return 'Token(%s %d %d %s)' % (self.text, self.start, self.end, self.quoted)

class ParsedVerb(ParsedToken):
    def __init__(self, verb, start, builtin=None, **kwargs):
        super(ParsedVerb, self).__init__(verb, start, **kwargs)
        self.resolved = not not builtin 
        self.builtin = builtin

    def resolve(self, resolution):
        self.resolved = True
        self.builtin = None #FIXME or delete

class CountingStream(object):
    def __init__(self, stream):
        super(CountingStream, self).__init__()
        self.__stream = stream
        self.__offset = 0
        self.__at_eof = False

    def read(self, c):
        result = self.__stream.read(c)
        resultlen = len(result)
        self.__offset += resultlen
        self.__at_eof = resultlen < c
        return result

    def at_eof(self):
        return self.__at_eof

    def get_count(self):
        return self.__offset

class Pipeline(gobject.GObject):
    """A sequence of Commands."""

    __gsignals__ = {
        "state-changed" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, []),
        "metadata" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_UINT, gobject.TYPE_PYOBJECT, gobject.TYPE_PYOBJECT, gobject.TYPE_PYOBJECT, gobject.TYPE_PYOBJECT)),        
        "exception" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,gobject.TYPE_PYOBJECT)),        
    }

    __ws_re = re.compile(r'\s+')

    def __init__(self, components, input_type='unknown', input_optional=False,
                 output_type='unknown', locality=None,
                 idempotent=False,
                 undoable=False):
        super(Pipeline, self).__init__()
        self.__components = components
        for component in self.__components:
            component.set_pipeline(self)
        self.__locality = locality
        self.__input_type = input_type
        self.__input_optional = input_optional
        self.__idempotent = idempotent
        self.__undoable = undoable
        self.__output_type = output_type
        self.__undo = []
        self.__cmd_metadata_lock = threading.Lock()
        self.__idle_emit_cmd_metadata_id = 0
        self.__cmd_metadata = {}
        self.__cmd_complete_count = 0
        self.__state = 'waiting'
        self.__completion_time = None
        
    def get_state(self):
        return self.__state     

    def disconnect(self):
        for cmd in self.__components:
            cmd.disconnect()
    
    def __execute_internal(self, force_sync, opt_formats=[]):
        _logger.debug("Executing %s", self)
        self.__set_state('executing')
        meta_idx = 0          
        for i,cmd in enumerate(self.__components):
            cmd.connect("complete", self.__on_cmd_complete)
            cmd.connect("exception", self.__on_cmd_exception)            
            # Here we record which commands include metadata, and
            # pass in the index in the pipeline for them.
            if cmd.builtin.get_hasmeta():
                _logger.debug("connecting to metadata on cmd %s, idx=%s", cmd, meta_idx)
                cmd.connect("metadata", self.__on_cmd_metadata, meta_idx)
                meta_idx += 1                
        prev_opt_formats = []
        for cmd in self.__components[:-1]:
            if cmd.input:
                cmd.input.negotiate(prev_opt_formats, cmd.get_input_opt_formats())
            prev_opt_formats = cmd.get_output_opt_formats()
            if cmd.out_redir:
                prev_opt_formats = []
        last = self.__components[-1]
        if not last.out_redir:
            last_opt_fmts = last.get_output_opt_formats()
        else:
            last_opt_fmts = []
        last.output.negotiate(last_opt_fmts, opt_formats)
        for i,cmd in enumerate(self.__components[:-1]):
            cmd.execute(force_sync)
        last.execute(force_sync)
        
    def validate_state_transition(self, state):
        if self.__state == 'waiting':
            return state in ('executing', 'exception')
        elif self.__state == 'executing':
            return state in ('complete', 'cancelled', 'exception')
        elif self.__state in ('cancelled', 'exception', 'undone'):
            return None
        elif self.__state == 'complete':
            return state in ('undone',) and self.get_undoable()
        assert(False)
        
    def is_complete(self):
        return self.__state in ('complete', 'cancelled', 'exception', 'undone')
        
    def __set_state(self, state):
        trans = self.validate_state_transition(state)
        if trans is None:
            _logger.debug("ignoring transition from state %s to %s", self.__state, state)
            return
        elif not trans:
            raise ValueError("Invalid state transition %s to %s", self.__state, state)
        
        self.__state = state
        if self.is_complete():
            self.__completion_time = time.time()         
        self.emit('state-changed')

    def execute(self, **kwargs):
        self.__execute_internal(False, **kwargs)

    def execute_sync(self, **kwargs):
        self.__execute_internal(True, **kwargs)

    def push_undo(self, fn):
        self.__undo.append(fn)

    def get_undoable(self):
        return self.__undoable

    def undo(self):
        for fn in self.__undo:
            fn()
        self.__set_state('undone')

    def get_completion_time(self):
        return self.__completion_time

    def get_idempotent(self):
        return self.__idempotent

    def get_status_commands(self):
        for cmd in self.__components:
            if cmd.builtin.get_hasstatus():
                yield cmd.builtin.name

    def __on_cmd_metadata(self, cmd, key, flags, meta, cmdidx):
        self.__cmd_metadata_lock.acquire()
        if self.__idle_emit_cmd_metadata_id == 0:
            self.__idle_emit_cmd_metadata_id = gobject.timeout_add(200, self.__idle_emit_cmd_metadata, priority=gobject.PRIORITY_LOW)
        self.__cmd_metadata[(cmd, cmdidx, key)] = (flags, meta)
        self.__cmd_metadata_lock.release()

    def __idle_emit_cmd_metadata(self):
        _logger.debug("signalling command metadata")      
        self.__cmd_metadata_lock.acquire()
        self.__idle_emit_cmd_metadata_id = 0
        meta_ref = self.__cmd_metadata
        self.__cmd_metadata = {}
        self.__cmd_metadata_lock.release()
        for (cmd,cmdidx,key),(flags,meta) in meta_ref.iteritems():
            self.emit("metadata", cmdidx, cmd, key, flags, meta)

    def __on_cmd_complete(self, cmd):
        _logger.debug("command complete: %s", cmd)
        if cmd.get_executing_sync():
            self.__idle_handle_cmd_complete(cmd)
        else:  
            gobject.idle_add(lambda: self.__idle_handle_cmd_complete(cmd))
        
    def __idle_handle_cmd_complete(self, cmd):
        self.__cmd_complete_count += 1
        if self.__cmd_complete_count == len(self.__components):
            self.__set_state('complete')

    def __on_cmd_exception(self, cmd, e):
        if not self.__state == 'executing':
            return        
        try:
            self.cancel(changestate=False)
        except:
            _logger.exception("Nested exception while cancelling")
            pass
        self.emit("exception", e, cmd)
        self.__exception_info = (e.__class__, str(e), cmd, traceback.format_exc())
        self.__set_state('exception')
        
    def get_exception_info(self):
        return self.__exception_info

    def get_output(self):
        return self.__components[-1].output

    def get_input_type(self):
        return self.__input_type

    def get_input_optional(self):
        return self.__input_optional

    def get_output_type(self):
        return self.__output_type

    def get_auxstreams(self):
        for cmd in self.__components:
            for obj in cmd.get_auxstreams():
                yield obj

    def cancel(self, changestate=True):
        if not self.__state == 'executing':
            return
        if changestate:
            self.__set_state('cancelled')        
        for component in self.__components:
            component.cancel()        

    def is_nostatus(self):
        return self.__components[0].builtin.nostatus

    def set_output_queue(self, queue, map_fn):
        self.__components[-1].set_output_queue(queue, map_fn)
        
    def set_input_queue(self, queue):
        # FIXME - remove this is_first bit
        self.__components[0].set_input(queue, is_first=True)

    def get_locality(self):
        return self.__locality

    @staticmethod
    def __streamtype_is_assignable(out_spec, in_spec, in_optional):
        if out_spec is None:
            return in_optional
        if in_spec in ('any', 'identity'):
            return True
        if out_spec == 'any':
            # An output of any can only connect to another any
            return False
        if out_spec is in_spec:
            return True
        for base in out_spec.__bases__:
            if base is in_spec:
                return True
        return False

    @staticmethod
    def mkparser(text):
        if isinstance(text, unicode):
            utext = text
        else:
            utext = unicode(text, 'utf-8')
        countstream = CountingStream(StringIO(utext))
        parser = shlex.shlex(countstream, posix=True)
        parser.wordchars += './[]{}~!@$%^&*()-_=+:;'
        return (countstream, parser)

    @staticmethod
    def tokenize(text, context=None, assertfn=None, accept_unclosed=False):
        result = []
        _logger.debug("parsing '%s'", text)
        
        (countstream, parser) = Pipeline.mkparser(text)
        
        is_initial = True
        first_token = None
        curpos = 0
        while True:
            try:
                (token, quoted) = parser.get_token_info()
            except ValueError, e:
                # FIXME gross, but...any way to fix?
                msg = hasattr(e, 'message') and e.message or (e.args[0])
                was_quotation_error = (e.message == 'No closing quotation' and parser.token[0:1] == "'")
                if (not accept_unclosed) or (not was_quotation_error):
                    _logger.debug("caught lexing exception", exc_info=True)
                    raise PipelineParseException(e)
                arg = parser.token[1:]
                if arg:
                    token = ParsedToken(arg, curpos+1, was_unquoted=True)
                    _logger.debug("handling unclosed quote, returning %s", token)
                    yield token
                    return
                else:
                    _logger.debug("handling unclosed quote, but token was empty")
                    return
            # empty input
            if token is None:
                break 
            is_initial = False
            end = countstream.get_count()
            if not quoted and token in ('|', '<', '>', '>>'):
                if token == '|':
                    yield hotwire.script.PIPE
                elif token == '>':
                    yield hotwire.script.REDIR_OUT
                elif token == '>>':
                    yield hotwire.script.REDIR_OUT_APPEND
                elif token == '<':
                    yield hotwire.script.REDIR_IN           
            else:
                if end-curpos > len(token):
                    end = curpos+len(token)
                yield ParsedToken(token, curpos, end=end, quoted=quoted)
            curpos = end
        
    @staticmethod
    def create(context, resolver, *tokens):
        if context is None:
            context = HotwireContext()
        components = []
        undoable = None
        idempotent = True
        prev = None
        pipeline_input_type = 'unknown'
        pipeline_input_optional = 'unknown'
        pipeline_output_type = None
        prev_locality = None
        pipeline_type_validates = True
        pushback = []
        tokens = list(tokens)
        is_first = True
        def pull_token():
            if pushback:
                return pushback.pop(0)
            else:
                return tokens.pop(0)            
        while tokens or pushback:
            builtin_token = pull_token()
            _logger.debug("token = %r", builtin_token)

            if is_first and builtin_token == hotwire.script.PIPE:
                _logger.debug("doing current rewrite")
                pushback.insert(0, builtin_token)                
                pushback.insert(0, 'current')
                continue
            is_first = False            
                
            def forcetoken(t):
                # Allow passing plain strings for convenience from Python.
                # Treat them as quoted.
                if isinstance(t, basestring):
                    return ParsedToken(t, -1, quoted=True)
                return t
            
            builtin_token = forcetoken(builtin_token)

            # Attempt to determine which builtin we're using
            if isinstance(builtin_token, Builtin):
                b = builtin_token
                cmdargs = []
            # If we're parsing without a resolver, assume we're using sys
            elif isinstance(builtin_token, ParsedToken):
                try:
                    b = BuiltinRegistry.getInstance()[builtin_token.text]
                    cmdargs = []
                except KeyError, e:
                    if resolver:
                        (b, cmdargs) = resolver(builtin_token.text)
                        _logger.debug("resolved: %r to %r %r", builtin_token.text, b, cmdargs)
                        if not b:
                            raise PipelineParseException(_('No matches for %s') % (gobject.markup_escape_text(builtin_token.text),))
                    else:
                        b = BuiltinRegistry.getInstance()['sys']
                        cmdargs = [ParsedToken(builtin_token.text, builtin_token.start, end=builtin_token.end)]
            elif builtin_token in (hotwire.script.PIPE, hotwire.script.REDIR_IN, hotwire.script.REDIR_OUT, hotwire.script.REDIR_OUT_APPEND):
                raise PipelineParseException(_("Unexpected token %d") % (builtin_token,))
            else:
                _logger.error("unknown in parse stream: %r", builtin_token)
                assert False
                
            # We maintain the set of all tokens we processed in the command so that the completion system can use them.
            alltokens = [builtin_token]
            cmdargs = map(forcetoken, cmdargs)            
            alltokens.extend(cmdargs)
                
            in_redir = None
            out_redir = None

            # Pull from the stream to get all the arguments
            while tokens:
                cmdarg = forcetoken(pull_token())
                if cmdarg == hotwire.script.PIPE:
                    break
                elif cmdarg == hotwire.script.REDIR_IN:
                    if not tokens:
                        raise PipelineParseException(_('Must specify target for input redirection'))
                    in_redir_token = pull_token()
                    in_redir = in_redir_token.text
                    alltokens.append(in_redir_token)
                elif cmdarg == hotwire.script.REDIR_OUT:
                    if not tokens:
                        raise PipelineParseException(_('Must specify target for output redirection'))                   
                    out_redir_token = pull_token()
                    out_redir = out_redir_token.text                     
                    alltokens.append(out_redir_token)               
                else:
                    alltokens.append(cmdarg)
                    cmdargs.append(cmdarg)         

            builtin_opts = b.get_options()
            def arg_to_opts(arg):
                if builtin_opts is None:
                    return False
                if arg.startswith('-') and len(arg) >= 2:
                    args = list(arg[1:])
                elif arg.startswith('--'):
                    args = [arg[1:]]
                else:
                    return False
                results = []
                for arg in args:
                    for aliases in builtin_opts:
                        if '-'+arg in aliases:
                            results.append(aliases[0])
                return results
            options = []
            expanded_cmdargs = []
            for token in cmdargs:
                # Treat quoted options as regular arguments
                if token.quoted:
                    expanded_cmdargs.append(CommandArgument(token.text, quoted=True))
                else:
                    argopts = arg_to_opts(token.text)
                    if argopts:
                        options.extend(argopts)
                    else:
                        expanded_cmdargs.append(token.text)
            cmdtokens = [builtin_token]
            cmdtokens.extend(cmdargs)
            cmd = Command(b, expanded_cmdargs, options, context, tokens=alltokens, in_redir=in_redir, out_redir=out_redir)
            components.append(cmd)
            if (not in_redir) and prev:
                cmd.set_input(prev.output)
            if pipeline_output_type:
                cmd.set_input_type(pipeline_output_type)
            input_accepts_type = cmd.builtin.get_input_type()
            input_optional = cmd.builtin.get_input_optional()
            if pipeline_input_optional == 'unknown':
                pipeline_input_optional = input_optional
            _logger.debug("Validating input %s vs prev %s", input_accepts_type, pipeline_output_type)

            if prev and not pipeline_output_type:
                raise PipelineParseException(_("Command %s yields no output for pipe") % \
                                             (prev.builtin.name))
            if (not prev) and input_accepts_type and not (input_optional): 
                raise PipelineParseException(_("Command %s requires input of type %s") % \
                                             (cmd.builtin.name, input_accepts_type))
            if input_accepts_type and prev \
                   and not Pipeline.__streamtype_is_assignable(pipeline_output_type, input_accepts_type, input_optional):
                raise PipelineParseException(_("Command %s yields '%s' but %s accepts '%s'") % \
                                             (prev.builtin.name, pipeline_output_type, cmd.builtin.name, input_accepts_type))
            if (not input_optional) and (not input_accepts_type) and pipeline_output_type:
                raise PipelineParseException(_("Command %s takes no input but type '%s' given") % \
                                             (cmd.builtin.name, pipeline_output_type))
            locality = cmd.builtin.get_locality()
            if prev_locality and locality and (locality != prev_locality):
                raise PipelineParseException(_("Command %s locality conflict with '%s'") % \
                                             (cmd.builtin.name, prev.builtin.name))
            prev_locality = locality
                
            if out_redir:
                prev = None
            else:
                prev = cmd
            if pipeline_input_type == 'unknown':
                pipeline_input_type = input_accepts_type

            if cmd.builtin.get_output_type() != 'identity':
                if context and cmd.builtin.get_output_typefunc():
                    pipeline_output_type = cmd.builtin.get_output_typefunc()(context)
                else:
                    pipeline_output_type = cmd.builtin.get_output_type()

            if undoable is None:
                undoable = cmd.builtin.get_undoable()
            elif not cmd.builtin.get_undoable():
                undoable = False

            if not cmd.builtin.get_idempotent():
                idempotent = False

        if undoable is None:
            undoable = False
        pipeline = Pipeline(components,
                            input_type=pipeline_input_type,
                            input_optional=pipeline_input_optional,
                            output_type=pipeline_output_type,
                            locality=prev_locality,
                            undoable=undoable,
                            idempotent=idempotent)
        _logger.debug("Parsed pipeline %s (%d components, input %s, output %s)",
                      pipeline, len(components),
                      pipeline.get_input_type(),
                      pipeline.get_output_type())
        return pipeline 

    @staticmethod
    def parse(text, context=None, resolver=None, accept_unclosed=False):
        tokens = list(Pipeline.tokenize(text, context, accept_unclosed=accept_unclosed))
        return Pipeline.create(context, resolver, *tokens)
    
    def __iter__(self):
        for component in self.__components:
            yield component
        
    def __getitem__(self, i):
        return self.__components[i]

    def __str__(self):
        return string.join(map(lambda x: x.__str__(), self.__components), ' | ')        
