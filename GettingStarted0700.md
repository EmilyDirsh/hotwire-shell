(Please use the [Discussion Group](http://groups.google.com/group/hotwire-shell) for any questions, and the [issue list](http://code.google.com/p/hotwire-shell/issues/list) for bug reports)

_This tutorial corresponds with Hotwire 0.710_.  For the 0.6xx series, see GettingStarted0600 (or upgrade!).

# Introduction to HotwirePipe #

You've started Hotwire for the first time, and are looking at a command prompt.  It wants us to type something.  Let's do it; type:

```
ls
```

What happened?  In short, Hotwire resolved "ls" to the **ls** Builtin object, executed it with no arguments in a thread, received the **File** objects it returned, and displayed them with the **FilePathRenderer**.

At the core of Hotwire is the idea of object-oriented pipeline processing.  On the top right of the display, you should see something that says "Type: GnomeVfsFile".  This is telling you that the current stream superclass is **GnomeVfsFile** objects.  If you expand the inspector, you can see the properties of the output objects.

You have access to those properties.  Let's try creating a pipeline:

```
ls | prop size
```

The **prop** builtin returns the property of an object.

Now, let's take a look at our process list:

```
proc | filter python cmd
```

This command will show you all processes whose **cmd** property matches the regular expression "python".  Let's ask for help about **proc**:

```
help proc
```

The text `in: None  out: <class 'hotwire.sysdep.proc.Process'>` is telling is that the **proc** builtin outputs **Process** objects.  Click on the link to see the inspector for that object class and its available properties.

Let's go back to manipulating files a bit more:

```
cd Desktop
ls -a *.zip
```

Here we can see that Hotwire's syntax is very shell-like in argument processing and globs.  Other things to try are Hotwire's builtin file management commands like **mv** and **rm**.  In particular **rm** is special in that it actually moves files to the Trash by default, which gives it support for undo.

# System commands #

You aren't limited to Hotwire's builtin commands like **ls** and **proc**.  You can also execute system programs using the **sys** builtin:

```
sys ifconfig
```

You'll notice that we got the result as text.  Now, we mentioned Hotwire is oriented around object-oriented pipeline processing.  What the **sys** builtin does is look up an external program as a Unix shell would, and then return its output as an object stream - in particular a stream of Unicode strings, one per line.  You can confirm this by noticing that the pipeline type in the top right is now `unicode`.

The above is very important to understand - again, in the Hotwire model, external binaries are just a type of command which return lines of text.

Because executing external binaries is quite common, Hotwire allows you to omit the **sys**:

```
ifconfig
```

If a verb typed in doesn't match the name of a builtin, Hotwire tries to execute it using **sys** by default.

For pure text processing, Hotwire actually has several advantages over a Unix terminal.  By default, the _entire_ output of every command is saved, and Hotwire knows which commands output what text.  This lets us do some neat things; for example, type:

```
|filter -i link
```

_Note the leading "|"_. What happened here?  When you start a pipeline with "|", Hotwire actually expands it to "current | ", which means "pipe the output of the currently visible command".  This lets you _interactively_ refine pipelines by chaining the output of a previous one into a new one, _without re-execution_.

Another perk Hotwire offers is Firefox-style search over text.  Press `Ctrl-s`.  You should see a search area appear.  Enter some text such as `link`, and use the up/down arrows to go between matches.

Press `ESC` when you're done.

# Overview mode and saved results #

As mentioned above, Hotwire is saving the result of every pipeline.  Currently, it saves them until 5 minutes after you last viewed them; then they are automatically garbage collected.  Try pressing `Ctrl-Shift-o` (or View->Overview) to see a complete list of all the saved results.

Click on one of them to display it.  From there, you can use `Ctrl-Down` and `Ctrl-Up` to move forwards and backwards through results, respectively.

# Everything is Asynchronous #

You might have noticed that commands never block your shell.  By default Hotwire runs everything under the equivalent of '&' in the Unix shell.  Try typing the following:

```
sleep 30
```

While it's running, you can continue to do other things.  This can be very convenient for things such as `make`, `svn up`, etc.

# Navigating completions and history #

At this point you've run a number of commands, and you may have seen the completion/history popup.  Recognizing that often day-to-day work can be repetitive - you might run the same commands very often in just a few directories - Hotwire is fanatical about remembering what you do and making it easy to find things again.

### Per-tab command history ###

Try pressing the `Up` navigational arrow.  This pops up the dialog for the per-tab command history.  Keep pressing Up or Down to select a history item, then Enter to choose.

### Token completions with TAB ###

Also, you might have already noticed that Hotwire is displaying choices for token completion and history if you've paused in typing.  Let's take a look.

Type the following, but _do not hit Return_ - instead hit `TAB` at the end:

```
ls
```

You should see a dialog that shows you all verbs which match `ls` - this is by default the Hotwire builtin **ls**, but other things such as `lspci` are offered as well.  Press `TAB` to expand the completion selections.  As above, `Enter` chooses one.

You can also use TAB to look for completions to your files and directories.  Try typing the following, then hit `TAB`:

```
ls ~/D
```

On a recent system you will likely see completions for at least `Desktop` and `Downloads`.  Again, once you're in a completion selection mode, use the up/down arrows to move the selection, and `Enter` to choose.

### History substring search ###

Additionally, Hotwire is automatically doing a search of your command history as you type.  Try the `ls` again, but this time press `Ctrl-R`:

```
ls
```

`Ctrl-R` shows you which commands you executed previously that match the current input.

# Running Python code #

One major goal of Hotwire is to bring real programming languages like Python and Ruby much closer to hand than is normally the case with a Unix terminal+shell.  Because Hotwire is built on the Python runtime, it has powerful execution and introspection capability.  Let's run some Python:

```
py 1+1
```

If you look above, you can see that Hotwire actually parsed this as `py-eval "1+1"`.  Hotwire knows about different languages, and allows you to run them using prefixes.

```
py import os; os.getpid()
```

Note here in particular you don't have to quote anything.  Hotwire is taking everything we type after "py " literally.

```
py xrange(20)
```

What's going on here is that because Hotwire is oriented around stream processing, it is expanding iterable python objects to streams of objects.

# Changing the input language #

If you are in a mode where you mainly want to enter Python without using "py " prefix repeatedly, you can change the input language using `Ctrl-Shift-L`, or by just clicking on the language chooser in the bottom left.

Change the input language to Python.  Then type:

```
2+2
```

The language selector causes Hotwire to treat your input as if you had typed the language prefix before each line.  Thus the above is equivalent to `py 2+2` in the HotwirePipe mode.  Switch back to HotwirePipe mode again by using `Ctrl-Shift-L` - we'll get to the other languages in a minute.

# Python snippets in HotwirePipe #

In the HotwirePipe language, you can use several builtins which can evaluate snippets of Python code.   These Python snippets act a bit like `lambda`, except that the variable `it` is bound to the object being processed.

```
ls | py-map 'it.path.upper() + "\n"'
```

The **py-map** builtin acts like the Python `map` function.  It allows you to transform an object stream.  Here, we're grabbing the `path` property of each **File** object, uppercasing it, and appending a newline.  We need the newline because otherwise the strings will appear all on one line in the **UnicodeRenderer** (in the future this will be easier to deal with).


```
proc | py-filter "it.pid > 50 and it.pid < 5000"
```

The **py-filter** builtin is like the Python function `filter`.  As with **py-map**, the variable `it` is bound to the current object.

```
ifconfig| py-map "it.swapcase()"
```

Remember, because this is the HotwirePipe language, we can easily execute system commands and pipe them to Python code.

# Evaluating Python scripts #

If you look at the implementation of Hotwire builtins, you'll notice that all of them are essentially just wrapped Python generator functions.  If you want to create anonymous scripts and see their output, you can do that with your chosen text editor and the **py-eval** builtin.

```
ed ~/testscript.py
```

Inside testscript.py, write:

```
import os,sys,time

def main():
  time.sleep(3)
  yield 42
  time.sleep(3)
  yield "Test python generator script!"
```

Now, save it and close the editor.  In Hotwire, type:

```
py-eval -f ~/testscript.py
```

The **py-eval** builtin looks inside the file for a function called `main`.  It then executes it as a generator.  You can put whatever Python code you want inside this file, and it will be compiled and executed inside the Hotwire process, making it easy to view and manipulate with further pipelines.

# Running other languages #

Python is a good programming language, but it is not the only language.  A true shell should be flexible, able to handle whichever language you want to use.  You may notice that we called the builtin **py-map**, and not just **map**.  This was deliberate - in the future, we'd like to have **rb-map** as well.  And **pl-filter**.

However, currently due to technical limitations, Hotwire best supports Python because it can be executed in-process.  In the medium-term future, we hope for a common shared runtime for Free Software programming languages, so that Hotwire can be more than just Python.

Despite this, there are still useful things we can do - we can communicate with other languages on a bytestream level.  So Hotwire has the concept of a language registry, which currently just has basically a favicon and an interpreter execution command for each language.  This turns out to allow some useful things.

For example, if you're a Ruby programmer - have you ever wished you could easily use Ruby in your Unix pipelines?  Let's go back to that `ifconfig` output:

```
ifconfig
```

We mentioned earlier that Python had the prefix `py`.  Similarly, Ruby has the prefix `rb`.

Now you can pipe the output of the last command to some Ruby:

```
|rb $stdin.each { |line| puts line.downcase }
```

If you run this, you see what happens is that Hotwire will pass it to the external Ruby interpreter using "ruby -e".  The large advantage of this over a traditional Unix shell is that you do not need to shell-quote your Ruby code - anything you type after the "|rb" will be passed directly to Ruby, with no Hotwire processing.

Hotwire also has several other languages registered by default.  For example, if you want to run a snippet of Unix shell, that's easy to do:

```
sh for x in $(seq 50); do sleep 0.5; echo ${x}; done
```

As with the Ruby example, Hotwire will pass everything you type after **sh** directly to `/bin/sh -c`.

# Giving input to commands #

So we've seen how Hotwire runs executables asynchronously in the background.  What if you need to give input to one?  Sometimes e.g. "svn up" might ask for a password.  Hotwire has some rudimentary support for input.  We can try it now:

Try running this small shell script, which reads from its standard input:

```
sh echo "Sample question? [y/n]"; read ans; echo "You answered ${ans}"
```

Press `Ctrl-I` to activate input mode.  This allows you to send basic lines of input to the subprocess.  For example:

```
y
```

When you're done, press `ESC` to exit input mode.

# Creating terminals #

A significantly smaller percentage of commands you might encounter are actually designed for the Unix terminal "GUI".  Examples include "vi", "mutt", and "top".

Hotwire also has a builtin called **term** which creates a full Unix terminal for commands.  Many popular Unix commands which require a terminal are by default aliased to `term commandname`.  For example, try typing:

```
top
```

What happened here is Hotwire expanded it using its default alias from `top` to `term top`.

This will create another tab with the command; when the command exits, the tab is removed.

You can see the default list of aliases by typing:

```
help
```

And scroll to the bottom.  For more on command compatibility, see HotwireCommandInput.

# Tutorial Ends #

You've now had your first twenty minutes or so with a hypershell.  There is a huge number of differences from a traditional Unix terminal+shell or Windows `cmd.exe`, but in the end you we hope find that your time invested in learning Hotwire pays itself back many times over.

# Further Resources #

You may be interested in HotwirePipeExamples for some more commands to try, and ExtendingHotwire for how to add custom Python to Hotwire.  You could also review the KeyboardShortcuts and CommandLineOptions .

See also HotwireArchitecture for a more technical overview of how things work.