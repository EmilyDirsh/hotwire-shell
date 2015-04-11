# This page is for Hotwire 0.6xx #

See GettingStarted0700 for the current version.

# Older tutorial #

(Please use the [Discussion Group](http://groups.google.com/group/hotwire-shell) for any questions, and the [issue list](http://code.google.com/p/hotwire-shell/issues/list) for bug reports)

This tutorial corresponds with Hotwire 0.620 and 0.600.

# Hotwire Basics #

## File Management ##

To start out, try using **ls** to list the contents of your home directory:

```
ls
```

Hotwire has support for Unix-style globbing:

```
ls *.png
```

Next, use **cd** to change to a subdirectory.  While you are typing, note you can hit `TAB`
to choose completions.

```
cd ~/Desktop
```

Use **cp** to copy a file of your choice to another name

```
cp SomePicture.png AnotherName.png
```

Note Hotwire's file operation commands have progress bars.

Another thing to try is Hotwire's _undo_ support for **rm**.

```
rm SomeFile.txt
```

Verify the file is gone using **ls** again if you like.  Now look under the _Control_ menu; note there is an _Undo_ option available.  Try that now, and verify that your file reappeared.  Also note that unlike Unix _rm_, Hotwire's bulitin **rm** takes no options (it automatically removes
directories for example, no need for `-r`).

There are a number of builtins related to files, such as **mv**, **edit**, and **mkdir**.

## Executing System commands ##

(The rest of this tutorial is written assuming you are on Unix)

The above are all builtin commands; they are written in pure Python and are portable to all platforms Hotwire runs on (currently Linux and Windows).  Now you can try running some system commands:

```
sh ifconfig
```

However, because typing **sh** a lot would be annoying, Hotwire allows you to omit it:

```
ifconfig
```

Now, try typing **Ctrl-s** to search the output.  Press _ESC_ when you're done.

This mode is the default - the vast majority of system commands on Unix or Windows do some operation and output text.  Hotwire therefore defaults to assuming this, runs commands in the background.  For example, type

```
sleep 10
```

Note that while the command is executing, you can go on and do other things.  The author has found this very convenient for processes such as `make`.  At any point, you can also press `Ctrl-Shift-o` (View->Overview) to get a high-level view of the state of your commands.  Also try pressing `Ctrl-Up` and `Ctrl-Down` to navigate your command history.

### Giving input to commands ###

Try running `python`:

```
python
```

While Hotwire's automatic job backgrounding is very convenient for most commands, there are the occasional ones which take some input.  Hotwire only supports a basic form of command input right now.

Press `Ctrl-I` to activate input mode.  This allows you to send basic lines of input to the subprocess.  For example:

```
1+1
```

When you're done, press `ESC`.  The author understands that this mode is somewhat suboptimal.  Future work will improve it; see below.

### Terminal compatibility ###

At this point it is important to understand that this default Hotwire mode for system commands (called **sh**) may not work for all of them; some commands on your system may require a real terminal.  Hotwire also has a builtin called **term** which creates a full Unix terminal for commands.  For example, try typing:

```
term top
```

This will create another tab with the command; when the command exits, the tab is removed.  By default, Hotwire includes a set of aliases for common Unix commands which do require a full terminal (including `top`; above it would have worked to just say `top`).

For more on command compatibility, see HotwireCommandInput.

## Pipelines ##

Hotwire supports more than simple commands; you can string together chains of them via the **|** symbol,
just like in Unix shell.  For example:

```
ifconfig | filter Link
```

**filter** is a Hotwire builtin that outputs objects which match a regular expression.  But note the
bold match highlighting!  This is because **filter** outputs **TextMatch** objects, which subclass Python's **str** class with match indices.

Let's see what happens when we use the Unix `grep` on Hotwire's **ls**:

```
ls | grep png
```

Why do we just see plain text?  It is because Unix `grep` only operates on text streams, so the **FilePath** objects output from **ls** are coerced into strings.

But let's try using **filter** with **ls**:

```
ls | filter png
```

## Other Hotwire builtins ##

Try typing:

```
proc
```

**proc** is a Hotwire builtin that outputs **Process** objects, not text strings.  Thus, we can display
their object properties neatly into columns.  Now, try:

```
proc | filter python cmd
```

Note the extra argument _cmd_ for **filter**.  What that means is to apply the filter to a particular
property of an object.  See HotwireArchitecture for a detailed explanation of this example.

## History and Completion ##

As you've followed the tutorial up until now, you've probably noticed the completion popup appearing over the text entry.  The completion area is divided into two sections:

  * Token completions
  * Command history

Token completions are available via the `TAB` key; they only expand one part of your command.  So if you're typing a command which takes a file name, Hotwire will offer you files that seem to match your current "token".

The command history area is more simplistic and global; as you type, Hotwire is doing a plain text search over all of your previously-entered commands.  You access this area with the `Up` and `Down` arrows.

A good strategy is that if you want to repeat a command you entered earlier, try to think of a unique substring that would find it, then hit the `Up` arrow followed by `Return`.

# Programming and Extending #

At this point, you should take a while to play around and just get a feel for the system.  Look at the **help** output to see what builtins are available, try creating some new tabs, play around with the command history, etc.

Once you're ready to move on, see ProgrammingAndExtending.