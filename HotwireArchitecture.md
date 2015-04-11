# Hotwire architecture #

## Introduction to pipelines ##

The fundamental unit of Hotwire is the concept of an object-oriented pipeline.  A pipeline is composed of a chain of Hotwire **Builtins**, which are Python classes with a specific API.

A Hotwire **Builtin** in general takes as input a stream of objects, a set of arguments and options, and yields another object stream.  All of this is optional though; for example some builtins such as `rm` (**RmBuiltin**), only operate on their argument list, and don't input or output anything.  Others don't take any arguments.

Let's start with a simple example, in the HotwirePipe language:

```
proc | filter -i walters owner_name
```

This example finds all processes on the system whose `owner_name` property matches the regular expression "walters".   Note that unlike a traditional text-line based Unix `/bin/sh` pipeline, this will not be misled by other extraneous text
which happens to match the input (no `grep -v grep`).

`proc` references the **ProcBuiltin** class, which is outputting a stream of **Process** objects.  `filter` references the **FilterBuiltin** class, which can take any input type, and will output the same type.  The `walters` and `owner_name` are string arguments for **FilterBuiltin**, and `-i` is processed as an option.

Don't be fooled by the similarity to Unix shell syntax - in this example everything is in the Hotwire process; there is no execution of external programs.

When you give this command to Hotwire, it looks up the names `proc` and `filter` in the registry, parses the options and argument list, and then executes it.  Each component of a pipeline is executed in a new thread.  These threads then simply call the **execute** method of each **Builtin** object, which takes a context, arguments, and options.

Because each builtin runs in its own thread, Hotwire internally uses threadsafe Queues to pipe objects from one thread to another.

But to make things more concrete, ignoring threading, the above pipeline is equivalent to this Python code:

```
import re
from hotwire.sysdep.proc import ProcessManager

prop_re = re.compile('walters')

for process in ProcessManager.getInstance().get_processes():
  if prop_re.search(process.owner_name):
    yield process
```

This may also be a bit clearer from looking at the [proc source](http://hotwire-shell.googlecode.com/svn/trunk/hotwire/builtins/proc.py) and the [filter source](http://hotwire-shell.googlecode.com/svn/trunk/hotwire/builtins/filter.py).

Unfortunately, for Hotwire we had to implement the code to list processes on a system, and create the **Process** object.  But if the Python distribution included this bit, the pipeline and builtins would just be a simpler syntax for accessing Python libraries.

This point is very important - the intent is that Hotwire builtins are mostly just _trivial wrappers_ around actual APIs which are intended to be used from Python.  They take arguments and options in a shell-like way tends to be more convenient.

### The `sys` builtin ###

So the current list of Hotwire builtins is all well and good; we can see files using **LsBuiltin**, processes using **ProcBuiltin**, do HTTP GETs using **HttpGetBuiltin**.  But sadly, not every aspect of the operating system has a nice Python API.  For example, there is no default Python API to query active network interfaces.  Or to list hardware devices.  Or to manipulate the X server resolution.  And the list goes on.

You may recognize these commands on most Unix/Linux systems as `ifconfig`, `lshal`, and `xrandr`.  Realistically, Hotwire can't immediately ship a version of every single one of these commands.  We'd like to be able to continue using them.

Enter the **SysBuiltin**.  The idea is pretty simple; it can execute external Unix/Linux binaries as subprocesses, returning their output conceptually as a stream of Unicode strings.

We now have a great deal of backwards compatibility with the existing operating system tools.  For example, we can execute:

```
xrandr --auto
```

This works exactly like you might expect.  The `/usr/bin/xrandr` program is executed with the argument `--auto`.  In general, if a verb isn't recognized as the name of a builtin, we try to resolve it using the system binaries.

And because we have a model for how system commands fit into the Hotwire pipeline, we can pipe the stream of strings from a system command to Hotwire builtins:

```
ifconfig | filter -i link
```

## Renderers ##

Now, having a stream of objects isn't that interesting if we just display them in the way the default Python toplevel would; you'd see something like:

```
<Process object at 0x5295802>
<Process object at 0x1285429>
<Process object at 0x5988975>
```

etc.  Layered on top of the Hotwire pipeline processing is an integrated graphical display and introspection system.  There is a class called **ObjectsRenderer** which is an abstract API for displaying a stream of objects.  The most important subclass is **TreeObjectsRenderer** which presents a treeview display of object properties.

Currently, there is a global object called **ClassRendererMapping** which maps from Python class -> Renderer.  When we create a pipeline, we try to determine statically using the information from the builtins which renderer to pick.  If this fails, we pick one based on the first object we see.