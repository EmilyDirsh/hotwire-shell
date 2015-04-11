# What is Hotwire? #

The goal of the Hotwire Shell project is to create a "hypershell" that is better than both the Unix terminal+shell and Windows PowerShell.  It is designed for developers and system administrators.

## How is Hotwire better than the Unix shell? ##

Considered from a modern perspective, the Unix terminal is two things.  First, it is a pure text display, suitable for applications like the Unix shell which can run programs that just output plain text.  Think `ls` (without colors) `dmesg`, `cat` (on plain text files), etc.  A much smaller percentage take lines of input for a question or two.

Secondarily, the Unix terminal is also a very poor GUI toolkit.  One might challenge this - how is the terminal also a GUI?  Here we are defining a GUI as one whose output is not suitable to be piped into another program.  And today there are just a few commonly used applications written for the terminal GUI.  Examples are `vi`, `mutt`, `man`, and various others.

The key idea behind Hotwire is that instead of piping byte streams as Unix does, Hotwire's builtin commands output and process (Python) objects.  Hotwire achieves compatibility with terminal GUI programs by aliasing them to the equivalent of `xterm commandname`, e.g. by default `vi` is an alias for `term vi`.

## How is Hotwire better than Windows PowerShell? ##

At the core of PowerShell is a very good idea - that your system shell+language is built on top of a real API.  But rather than try to reuse an existing language like Python or Ruby, PowerShell is oriented solely towards its own language.  Secondly, PowerShell has a very poor user interface out of the box.  There are third-party interfaces, but I believe Hotwire proves that it's possible to do better if the shell, language, and GUI are all designed in conjunction and integrated together.

# Object pipeline processing #

At its core, Hotwire is based on the idea of asynchronously processing streams of objects.  Hotwire's builtin commands are typically just small wrappers around actual programming APIs.  For example, the Hotwire **proc** builtin outputs **Process** objects.  The **ls** builtin outputs **File** objects.  The **http-get** builtin returns a !HTTPResponse object from the Python standard library.

For example:

```
ls | prop size
```

This pipeline returns the _size_ property of each object.  Another example:

```
proc | filter python cmd
```

Outputs **Process** objects whose _cmd_ property matches the regular expression "python".

This default input language is called "HotwirePipe".  It's fairly basic, but a great number of problems can be expressed in this piping syntax.

Hotwire also lets you evaluate real Python code in a number of ways.  For example, you can use the **py-map** builtin in the HotwirePipe to transform an object stream.  Secondly, you can use **py-eval** to run arbitrary code from a file or argument.

## Text streams using the sys builtin ##

So what about compatibility with system commands like `ifconfig`, `make`, etc. on Unix?  Hotwire has a builtin called **sys**, which runs an external binary, returning its output as a stream of lines (in Unicode).  This gives Hotwire a great deal (but not complete) compatibility with previous operating system shells.  Hotwire will pull all system binaries into its command namespace, although Hotwire builtins override them.