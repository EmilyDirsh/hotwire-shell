# This page is obsolete #

This page is now obsolete; the best pages to look at is [GettingStarted](GettingStarted.md) and  [ExtendingHotwire](ExtendingHotwire.md).

# Historical content #

# Programming and Extending #

The goal of Hotwire is more than just being a somewhat nicer interface for running system commands; the intent is to be a fully programmable and extensible shell using Python.

## Learning Python ##

This tutorial assumes that you have a rudimentary familiarity with the [Python](http://python.org) programming langauge; if that's not the case, you can try [The Python Tutorial](http://docs.python.org/tut/tut.html).  Note that tutorial assumes you're running it from a system terminal; you can do `Ctrl-Shift-T` to get one.  However, you may also find Hotwire's builtin Python workpad to be useful (menu item _Tools_ -> _Python Workpad_).

## How Hotwire works ##

You've seen how Hotwire can display nicer icons for files and such; how does this work?  The answer is that **ls** is a Hotwire builtin which doesn't output raw text; instead, it outputs **FilePath** objects.  All hotwire commands are object pipelines.

For a better description of this, browse HotwireArchitecture.

At this point, you should be ready to code some Python.

## Combining Hotwire pipelines with Python code ##

Type the following:

```
sleep 10000
proc
py
```

The **py** builtin is new - it allows you to manipulate the results of the current pipeline with arbitrary Python code.

You should have a `sleep` process running in the background, a list of processes displayed in the main window, and a new editor window, ready to accept Python code.
Note here that Hotwire says:

```
# input type: <class 'hotwire.sysdep.proc.Process'>
```

This is telling us that our code is manipulating **Process** objects.  As a first try, let's use the builtin **outln** function to print things to the output window:

```
for obj in curshell.get_current_output():
  outln(obj)
```

Now, press `Control-Return` (or _Tools_ -> _Eval_ ).  You will currently get a text output window.  There are plans to extend this so that you can get the same nice object display that pipelines typed in the main Hotwire window have.

Extending our code a bit to find our `sleep` process:

```
for obj in curshell.get_current_output():
  if obj.owner_name == 'walters' and obj.cmd.find('sleep') >= 0:
    outln(obj)
```

Be sure to change `walters` to your user name.

Of course, you aren't limited to just printing out things; you can type any Python code you can think of.  For example, get a list, turn them all into uppercase, and write them to a file:

```
import tempfile
objs = map(lambda x: x.cmd.upper(), curshell.get_current_output())
(fd,tmppath) = tempfile.mkstemp('.tmp', 'hotwireout')
f = os.fdopen(fd, 'w')
for x in objs:
  f.write(x)
  f.write('\n')
f.close()
outln(tmppath)
```

Then press `Control-Return` again, and copy-paste the resulting filename back into the main Hotwire window, and type:

```
cat /tmp/hotwireout85So3e.tmp
```

# Extending Hotwire #

Ready to move on to ExtendingHotwire with permanent Python code?