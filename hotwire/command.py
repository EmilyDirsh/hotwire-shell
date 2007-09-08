import os, sys, threading, Queue, logging, string, re, time, shlex

import gobject

import hotwire.fs
from hotwire.async import CancellableQueueIterator, IterableQueue, MiniThreadPool
from hotwire.builtin import BuiltinRegistry
import hotwire.util
from hotwire.util import quote_arg

_logger = logging.getLogger("hotwire.Command")

class HotwireContext(gobject.GObject):
    __gsignals__ = {
        "cwd" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_STRING,)),
    }
    """The interface to manipulating a Hotwire execution shell.  Items
    such as the current working diretory may be changed via this class,
    and subclasses define further extended commands."""
    def __init__(self, initcwd=None):
        super(HotwireContext, self).__init__()
        self.chdir(initcwd or os.path.expanduser('~'))
        _logger.debug("Context created, dir=%s" % (self.get_cwd(),))

    def chdir(self, dir):
        dir = os.path.expanduser(dir)
        newcwd = os.path.isabs(dir) and dir or os.path.join(self.__cwd, dir)
        newcwd = os.path.normpath(newcwd)
        os.stat(newcwd) # lose on nonexistent
        self.__cwd = newcwd
        self.emit("cwd", newcwd)
        return self.__cwd

    def get_cwd(self):
        return self.__cwd

    def info_msg(self, msg):
        print msg

    def get_last_output(self):
        return None

class CommandContext(object):
    """An execution snapshot for a Command.  Holds the working directory
    when the command started, the input stream, and allows accessing
    the execution context."""
    def __init__(self, hotwire):
        self.input = None
        self.pipeline = None
        self.cwd = hotwire.get_cwd()
        self.last_output = hotwire.get_last_output()
        self.hotwire = hotwire
        self.__auxstreams = {}
        self.__status_notify_handler = None
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

    def set_status_notify(self, fn):
        self.__status_notify_handler = fn

    def status_notify(self, status, progress=-1):
        if self.__status_notify_handler:
            self.__status_notify_handler(status, progress)

class CommandQueue(IterableQueue):
    def __init__(self):
        IterableQueue.__init__(self)
        self.opt_type = None

    def negotiate(self, out_fmts, in_fmts):
        for fmt in out_fmts:
            if fmt in in_fmts:
                self.opt_type = fmt
                _logger.debug("Negotiated optimized type %s", fmt)
                break

class CommandAuxStream(object):
    def __init__(self, command, schema):
        self.command = command
        self.name = schema.name
        self.schema = schema
        self.queue = CommandQueue()

class CommandException(Exception):
    pass

class Command(gobject.GObject):
    """Represents a complete executable object in a pipeline."""

    __gsignals__ = {
        "status" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_STRING, gobject.TYPE_INT)),
        "exception" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
    }

    def __init__(self, builtin, args, hotwire):
        super(Command, self).__init__()
        self.builtin = builtin
        self.context = CommandContext(hotwire) 
        for schema in self.builtin.get_aux_outputs():
            self.context.attach_auxstream(CommandAuxStream(self, schema))
        if self.builtin.get_hasstatus():
            self.context.set_status_notify(lambda *args: self.emit("status", *args))
        self.output = CommandQueue()
        self.map_fn = lambda x: x
        self.args = args

        self._cancelled = False

    def set_pipeline(self, pipeline):
        self.context.set_pipeline(pipeline)

    def set_input(self, input):
        self.input = input and CancellableQueueIterator(input)        
        self.context.input = self.input
        
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

    def execute(self, **kwargs): 
        MiniThreadPool.getInstance().run(lambda: self.__run(**kwargs))

    def execute_sync(self, **kwargs):
        self.__run(**kwargs)

    def set_output_queue(self, queue, map_fn):
        self.output = queue
        self.map_fn = map_fn

    def get_auxstreams(self):
        for obj in self.context.get_auxstreams():
            yield obj

    def __run(self, opt_format=None):
        if self._cancelled:
            _logger.debug("%s cancelled, returning", self)
            self.output.put(self.map_fn(None))
            return
        try:
            builtin_opts = self.builtin.get_options()
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
        
            if builtin_opts is not None:
                options = []
            else:
                options = None
            if self.builtin.get_parseargs() == 'shglob':
                matched_files = []
                oldlen = 0
                for globarg_in in self.args:
                    argopts = arg_to_opts(globarg_in)
                    if argopts:
                        options.extend(argopts)
                        continue
                    globarg = os.path.expanduser(globarg_in)
                    matched_files.extend(hotwire.fs.dirglob(self.context.cwd, globarg))
                    newlen = len(matched_files)
                    if oldlen == newlen:
                        matched_files.append(globarg)
                        newlen += 1
                    oldlen = newlen    
                target_args = [map(lambda arg: hotwire.fs.FilePath(arg, self.context.cwd), matched_files)]
            else:
                target_args = []
                for arg in self.args:
                    argopts = arg_to_opts(arg)
                    if argopts:
                        options.extend(argopts)
                    else:
                        target_args.append(arg)
            _logger.info("Execute '%s' args: %s options: %s", self.builtin, target_args, options)
            kwargs = {}
            if options:
                kwargs['options'] = options
            if opt_format:
                kwargs['in_opt_format'] = in_opt_format
                _logger.debug("chose optimized format %s", opt_format)
            for result in self.builtin.execute(self.context, *target_args, **kwargs):
                # if it has status, let it do its own cleanup
                if self._cancelled and not self.builtin.get_hasstatus():
                    _logger.debug("%s cancelled, returning", self)
                    self.output.put(self.map_fn(None))
                    return
                self.output.put(self.map_fn(result))
        except Exception, e:
            _logger.exception("Caught exception: %s", e)
            self.emit("exception", e)
        self.output.put(self.map_fn(None))

    def __str__(self):
        return self.builtin.name + " " + string.join(map(unicode, self.args), " ")

class PipelineParseException(Exception):
    pass

class ParsedToken(object):
    def __init__(self, text, start, end=None, was_unquoted=False):
        self.text = text 
        self.start = start
        self.end = end or (start + len(text))
        self.was_unquoted = was_unquoted

    def __repr__(self):
        return 'Token(%s %d %d)' % (self.text, self.start, self.end)

class ParsedVerb(ParsedToken):
    def __init__(self, verb, start, builtin=None, **kwargs):
        super(ParsedVerb, self).__init__(verb, start, **kwargs)
        self.resolved = not not builtin 
        self.builtin = builtin

    def resolve(self, resolution):
        self.resolved = True
        self.builtin = None #FIXME or delete

class Pipeline(gobject.GObject):
    """A sequence of Commands."""

    __gsignals__ = {
        "status" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_UINT, gobject.TYPE_PYOBJECT, gobject.TYPE_STRING, gobject.TYPE_INT)),
        "exception" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, gobject.TYPE_PYOBJECT)),
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
        self.__cmd_statuses_lock = threading.Lock()
        self.__idle_emit_cmd_status_id = 0
        self.__cmd_statuses = {}

    def disconnect(self):
        for cmd in self.__components:
            cmd.disconnect()
    
    def __execute_internal(self, func, opt_formats=[]):
        _logger.debug("Executing %s", self)
        for cmd in self.__components:
            cmd.connect("exception", self.__on_cmd_exception)
            cmd.connect("status", self.__on_cmd_status)
        prev_opt_formats = []
        for cmd in self.__components[:-1]:
            cmd.output.negotiate(prev_opt_formats, cmd.get_input_opt_formats())
            func(cmd)
            prev_opt_formats = cmd.get_output_opt_formats()
        last = self.__components[-1] 
        last.output.negotiate(prev_opt_formats, opt_formats)
        func(last)

    def execute(self, **kwargs):
        self.__execute_internal(Command.execute, **kwargs)

    def execute_sync(self, **kwargs):
        self.__execute_internal(Command.execute_sync, **kwargs)

    def push_undo(self, fn):
        self.__undo.append(fn)

    def get_undoable(self):
        return self.__undoable

    def undo(self):
        for fn in self.__undo:
            fn()

    def get_idempotent(self):
        return self.__idempotent

    def get_status_commands(self):
        for cmd in self.__components:
            if cmd.builtin.get_hasstatus():
                yield cmd.builtin.name

    def __on_cmd_status(self, cmd, text, progress):
        self.__cmd_statuses_lock.acquire()
        if self.__idle_emit_cmd_status_id == 0:
            self.__idle_emit_cmd_status_id = gobject.timeout_add(200, self.__idle_emit_cmd_status, cmd, priority=gobject.PRIORITY_LOW)
        self.__cmd_statuses[cmd] = (text, progress)
        self.__cmd_statuses_lock.release()

    def __idle_emit_cmd_status(self, cmd):
        self.__cmd_statuses_lock.acquire()
        self.__idle_emit_cmd_status_id = 0
        text, progress = self.__cmd_statuses[cmd]
        self.__cmd_statuses_lock.release()
        cmd_idx = 0 
        for i,c in enumerate(self.__components):
            if cmd == c:
                break
            if c.builtin.get_hasstatus():
                cmd_idx += 1
        self.emit("status", cmd_idx, cmd, text, progress)

    def __on_cmd_exception(self, cmd, e):
        try:
            self.cancel()
        except:
            _logger.exception("Nested exception while cancelling")
            pass
        gobject.idle_add(lambda: self.emit("exception", cmd, e))

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

    def cancel(self):
        for component in self.__components:
            component.cancel()

    def is_nostatus(self):
        return self.__components[0].builtin.nostatus

    def set_output_queue(self, queue, map_fn):
        self.__components[-1].set_output_queue(queue, map_fn)

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
    def parse_tree(text, context, assertfn=None, accept_unclosed=False):
        """
        emacs
          => [
              [('Verb', 0, 4, None, 'unresolved')  # default is VerbCompleter
              ]
             ]
        emacs /tmp/foo.txt
          => [
              [('Verb', 0, 4, None, 'unresolved'),
               ('Arg', 5, 16, None)   # default is PathCompleter
              ]
        ps | grep whee <CURSOR>
          => [
              [('Verb', 0, 3, None)
              ],
              [('Verb', 21, 25, None),
               ('Arg', 27, 31, [])  # no completions
               ('Arg', 29, 29, [PropertyCompleter(class=UnixProcess)])
              ]
"""
        result = []
        pipeline_items = text.split(" | ")
        if pipeline_items[0] == '':
            return result

        curpos = 0
        for item in pipeline_items:
            if curpos != 0:
                curpos += 3 # previous pipe
            cmd_tokens = []
            parsed = item.split(' ', 1)
            if len(parsed) == 2:
                verb, rest = parsed
            else:
                verb = parsed[0]
                rest = ''
            try:
                builtin = BuiltinRegistry.getInstance()[verb]
                verb_token = ParsedVerb(verb, curpos, builtin=builtin)
                parseargs = builtin.get_parseargs()
            except KeyError, e:
                builtin = None
                verb_token = ParsedVerb(verb, curpos)
                parseargs = 'ws-parsed' 
            curpos = verb_token.end
            cmd_tokens.append(verb_token)
            if rest != '':
                # space we skipped over earlier
                curpos += 1
                _logger.debug("lexing '%s'", rest)
                parser = shlex.shlex(rest, posix=True)
                # We don't interpret any of these characters.
                # Thus, no need to regard them as separate tokens
                parser.wordchars += './~,*\\-$()&^%@`+=><?:;!{}[]'
                try:
                    arg = parser.get_token()
                    _logger.debug("parsed initial token '%s'", arg)
                    had_args = not not arg
                    while arg:
                        skipquote = False
                        if arg[0] == "'" and arg[-1] == "'":
                            arg = arg[1:-1]
                            skipquote = True
                        token = ParsedToken(arg, curpos + (skipquote and 1 or 0))
                        curpos = token.end+1+(skipquote and 1 or 0)
                        cmd_tokens.append(token)
                        arg = parser.get_token()
                        _logger.debug("parsed token '%s'", arg)
                    if had_args:
                        curpos -= 1 # we account for other space above
                except ValueError, e:
                    # FIXME gross, but...any way to fix?
                    was_quotation_error = (e.message == 'No closing quotation' and parser.token[0] == "'")
                    if (not accept_unclosed) or (not was_quotation_error):
                        _logger.debug("caught lexing exception", exc_info=True)
                        raise PipelineParseException(e)
                    arg = parser.token[1:] 
                    if arg:
                        token = ParsedToken(arg, curpos + 1, was_unquoted=True)
                        _logger.debug("handling unclosed quote, returning %s", token)
                        cmd_tokens.append(token)
                    else:
                        _logger.debug("handling unclosed quote, but token was empty")

            _logger.debug("%d tokens in command", len(cmd_tokens))                
            result.append(cmd_tokens)
        for cmd in result:
            for arg in cmd:
                assert(text[arg.start:arg.end], arg.text)
        return result

    @staticmethod
    def reparse_tree(tree, context):
        text = string.join([string.join([x.text for x in cmd], " ") for cmd in tree], " | ")
        return Pipeline.parse_tree(text, context)
            
    @staticmethod
    def parse_from_tree(tree, context=None):
        components = []
        undoable = None
        idempotent = True
        prev = None
        pipeline_input_type = 'unknown'
        pipeline_input_optional = 'unknown'
        pipeline_output_type = None
        prev_locality = None
        pipeline_type_validates = True
        for cmd_tokens in tree:
            verb = cmd_tokens[0]
            assert verb.resolved

            b = BuiltinRegistry.getInstance()[verb.text] 
            parseargs = b.get_parseargs()
            args_text = [x.text for x in cmd_tokens[1:]] 
            if parseargs == 'str':
                args = [string.join(args_text, " ")] # TODO syntax
            elif parseargs == 'str-shquoted':
                args = [string.join(map(quote_arg, args_text), " ")]
            elif parseargs in ('ws-parsed', 'shglob'):
                args = args_text 
            else:
                assert False
            cmd = Command(b, args, context)
            components.append(cmd)
            if prev:
                cmd.set_input(prev.output)
            input_accepts_type = cmd.builtin.get_input_type()
            input_optional = cmd.builtin.get_input_optional()
            if pipeline_input_optional == 'unknown':
                pipeline_input_optional = input_optional
            _logger.debug("Validating input %s vs prev %s", input_accepts_type, pipeline_output_type)

            if prev and not pipeline_output_type:
                raise PipelineParseException("Command %s yields no output for pipe" % \
                                             (prev.builtin.name))
            if (not prev) and input_accepts_type and not (input_optional): 
                raise PipelineParseException("Command %s requires input of type %s" % \
                                             (cmd.builtin.name, input_accepts_type))
            if input_accepts_type and prev \
                   and not Pipeline.__streamtype_is_assignable(pipeline_output_type, input_accepts_type, input_optional):
                raise PipelineParseException("Command %s yields '%s' but %s accepts '%s'" % \
                                             (prev.builtin.name, pipeline_output_type, cmd.builtin.name, input_accepts_type))
            if (not input_optional) and (not input_accepts_type) and pipeline_output_type:
                raise PipelineParseException("Command %s takes no input but type '%s' given" % \
                                             (cmd.builtin.name, pipeline_output_type))
            locality = cmd.builtin.get_locality()
            if prev_locality and locality and (locality != prev_locality):
                raise PipelineParseException("Command %s locality conflict with '%s'" % \
                                             (cmd.builtin.name, prev.builtin.name))
            prev_locality = locality
                
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
    def parse(str, context=None):
        return Pipeline.parse_from_tree(Pipeline.parse_tree(str, context), context)

    def __str__(self):
        return string.join(map(lambda x: x.__str__(), self.__components), ' | ')        

class MinionPipeline(gobject.GObject):

    __gsignals__ = {
        "exception" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, gobject.TYPE_PYOBJECT)),
    }

    def __init__(self, minion, pipeline_str, context=None):
        super(MinionPipeline, self).__init__()
        self.__minion = minion
        self.__channel = minion.open_channel()
        self.__channel_event_queue = CancellableQueueIterator(self.__channel.event_queue) 
        self.__pipeline_str = pipeline_str
        self.__pipeline_id = -1
        self.__result_queue = IterableQueue()

    def execute(self):
        MiniThreadPool.getInstance().run(self.__pipeline_com)

    def execute_sync(self):
        raise NotImplementedError()

    def cancel(self):
        self.__channel_event_queue.cancel()
        raise NotImplementedError() # need to cancel minion stuff

    def is_nostatus(self):
        return False

    def get_output_type(self):
        return str # for now

    def __pipeline_com(self):
        self.__channel.invoke('create_pipeline', self.__pipeline_str)
        for event in self.__channel_event_queue:
            if event.name == 'PipelineObject':
                pipeid = event.args[0]
                clsname = event.args[1]
                strval = event.args[2]
                #obj = RemoteObjectFactory.getInstance().load(event.args[0], event.args[1],
                #                                            event.args[2:])
                self.__result_queue.put(strval)
            elif event.name == 'PipelineComplete':
                _logger.debug("Got pipeline complete for %s", self.__pipeline_str)
                self.__result_queue.put(None)
                break

    def get_output(self):
        return self.__result_queue

    @staticmethod
    def parse(minion, text, context=None):
        return MinionPipeline(minion, text)

    def __str__(self):
        return '[%s] %s' % (self.__minion, self.__pipeline_str)
