# Current #

## Changes in Hotwire 0.721 ##

Visible changes:

  * Major UI streamlining; much more space is given to output display by default
  * Change terminal launch handling consistently; now all apps spawn in a new window, and Return closes them when they're done.
  * Improved exception handling; can now click to see full backtrace
  * Improved handling of singleton Python values
  * New builtin API, can define builtins as just decorated Python functions
  * In **py-eval** the variable `it` is bound to the currently visible value
  * **py-eval** can take input
  * Win32: Use native icons (Zeng.Shixin, [issue 165](https://code.google.com/p/hotwire-shell/issues/detail?id=165))
  * Win32: Get correct mimetype (Zeng.Shixin)
  * UnicodeRenderer gains match highlighting (Chris Mason, [issue 149](https://code.google.com/p/hotwire-shell/issues/detail?id=149))
  * New **pprint** builtin
  * New **head** builtin which operates on objects
  * **rm** can take **File** objects as input
  * Allow possibly type-unsafe pipelines such as `ls | prop path | grep foo` (the pipeline system is not yet smart enough to know that `path` is a string)
  * Added `argspec` property of Builtins; argument count checking is now part of the core, and all current builtins specify their possible arguments.
  * **help** displays possible arguments for builtins
  * UnicodeRenderer gains right click "Save output as..." option
  * Pipeline typechecking supports deep inheritance (Mark Williamson, [issue 147](https://code.google.com/p/hotwire-shell/issues/detail?id=147))
  * Improved lost connection handling display in HotSSH
  * `term htop`, `term most` by default

Notable bugfixes:

  * Avoid hang if pipeline takes 'any' as input
  * Don't crash on in-use-files on Windows (Zeng.Shixin, [issue 131](https://code.google.com/p/hotwire-shell/issues/detail?id=131))
  * Avoid GTK+ bug causing crash on right-click in HotSSH/HotSudo ([issue 151](https://code.google.com/p/hotwire-shell/issues/detail?id=151))
  * **fsearch** ignores non-Unicode files
  * Use system webbrowser.py on Windows ([issue 145](https://code.google.com/p/hotwire-shell/issues/detail?id=145))

## Changes in Hotwire SVN (Not released) ##

(As of [r1173](https://code.google.com/p/hotwire-shell/source/detail?r=1173))

None yet.

# Older releases #

## Changes in Hotwire 0.710 ##

Visible Changes:

  * Internal line processing includes newlines ([issue 111](https://code.google.com/p/hotwire-shell/issues/detail?id=111))
  * Import `~/.bash_history` (TiagoMatos)
  * Non-UTF8 locale handling (cgwalters, Zeng.Shixin, [issue 125](https://code.google.com/p/hotwire-shell/issues/detail?id=125), [issue 133](https://code.google.com/p/hotwire-shell/issues/detail?id=133))
  * Sorting on file renderer (schroed, [issue 119](https://code.google.com/p/hotwire-shell/issues/detail?id=119))
  * Open action now works on Windows (Zeng.Shixin)
  * New **apply** builtin ([issue 80](https://code.google.com/p/hotwire-shell/issues/detail?id=80))
  * New **view** builtin which launches editor in read-only mode
  * **kill** now optionally takes Process objects as input
  * **rm** has new `--unlink` option to really delete
  * `more` is now aliased to `term -w more` by default to avoid vanishing on small files
  * Completions popup only appears when it has something to show ([issue 135](https://code.google.com/p/hotwire-shell/issues/detail?id=135))
  * Hotwire Edit gains line numbers, goto line functionality

Notable Bugfixes:

  * HotSSH keybinding and focus issues fixed
  * Various Windows bugfixes (Zeng.Shixin, cgwalters)
  * Symbolic links handled better (schroed, [issue 120](https://code.google.com/p/hotwire-shell/issues/detail?id=120), [issue 121](https://code.google.com/p/hotwire-shell/issues/detail?id=121))
  * Don't error if process ends while input is open
  * Avoid lockup if completion throws an error (e.g. permission denied on directory)
  * History is saved asynchronously for improved interactivity during heavy disk I/O ([issue 88](https://code.google.com/p/hotwire-shell/issues/detail?id=88))

API Changes:

  * You should now register custom builtins using the `register_user` function of `BuiltinRegistry`.  Builtins shipped with the operating system can use `register_system`.

## Changes in Hotwire 0.700 ##

Hotwire has transitioned to its first **alpha** release; while it is still in development and a number of things may change, it is expected that significantly more people will find it to be a compelling replacement for terminal+shell.

The project has expanded in scope slightly; Hotwire now includes application-specific terminal containers.  Currently there are separate `hotwire-ssh` and a `hotwire-sudo` executables which have app-specific menu items and other features (e.g. `hotwire-ssh` has "New tab for connection" and "Open SFTP" options).  Note in Hotwire **ssh** is by default aliased to `hotwire-ssh` and likewise for **sudo**; you can also use these independently of Hotwire in a legacy Unix terminal+shell as well.

There are a few major changes to the core which bear longer explanation.  First, Hotwire is now a multi-language shell.  The old language is replaced by a rewritten "HotwirePipe" language.  It supports the object-oriented pipeline, and has also gained file I/O redirection - crucially, HotwirePipe no longer involves processing through `/bin/sh` for system commands.  Hotwire now also supports directly entering Python expressions and evaluating them in the shell, and visualizing their values.  In addition, Hotwire now has a syntax for executing code in other programming languages like Perl and Ruby using their external interpeters in a convenient syntax.

Second, many will be happy to discover the completion system has been entirely replaced and is now more bash-like; this closes a swath of issues ([issue 12](https://code.google.com/p/hotwire-shell/issues/detail?id=12), [issue 16](https://code.google.com/p/hotwire-shell/issues/detail?id=16), [issue 25](https://code.google.com/p/hotwire-shell/issues/detail?id=25), [issue 27](https://code.google.com/p/hotwire-shell/issues/detail?id=27)).  Your key habits will have to be relearned, but this should be for the better.

Another project-wide change is that the execution core and underlying libraries have been relicensed to a permissive MIT-style license (the user interface remains GPL).  This change was made with an eye to eventually including in the main Python distribution parts of the Hotwire core as an embedded system scripting language, as well as libraries such as Process enumeration.

Finally, Hotwire now runs again on Python 2.4, and should have improved compatibility with earlier GTK+/GNOME releases.

Visible Changes:

  * New pipeline class inspector sidebar, as well as object inspector window
  * History search is now on `Ctrl-r`
  * Completion status waits for a typing pause before appearing
  * Support for changing EDITOR used in environment (Preferences->Editor)
  * "View->To Window" menu item is now "File->Detach Tab"
  * New "Detach Command" menu item in Hotwire mode detaches just a single command (e.g. create a new window with just your `make` output)
  * Add "Quick Switch" dialog for searching most-used directories
  * Added popup menu on command headers
  * Unicode renderer wraps lines by default (right click to unset)
  * Unicode renderer has extended popup menu items
  * File renderer now supports interactive search
  * File context menu has icons for application launchers
  * "Move to Trash" context menuitem is replaced with more general "Copy Path to Input"
  * Added Back/Forward buttons and a "Go" menu ([issue 57](https://code.google.com/p/hotwire-shell/issues/detail?id=57))
  * Added "Remove Pipeline" menu item (with matching Undo support)
  * Command garbage collection is based on view time, not completion time
  * Support for bookmarking directories (using `.gtk-bookmarks`)
  * Added Fullscreen menu item
  * New **selection** builtin which outputs currently selected objects
  * **ed** launches your $EDITOR, not desktop environment text/plain editor
  * **ls** builtin outputs **File** objects, not **FilePath**
  * Removed Python Workpad; it is replaced by "py-eval -f".
  * New **py-map** builtin for processing using Python expression
  * New **py-filter** builtin allows filtering using Python expression
  * New **walk** builtin which recurses a directory yielding **File** objects
  * New **http-get** builtin does an HTTP GET and returns an `HTTPResponse` object
  * New **replace** builtin (Kevin Kubasik)
  * New **setenv** builtin
  * HotwireEdit supports "Save as", syntax highlighting, inline search
  * Use Unix filesystem backend on FreeBSD.
  * More default **term** commands: `ipython`
  * Cancel now sends SIGTERM rather than SIGINT
  * **help** shows installed languages
  * **help** shows both builtin alias names, and textual alias expansion
  * **help** has hyperlinks to launch inspector for relevant objects

Notable Bugfixes:
  * Some memory leaks plugged
  * Automatically enter password mode if pty echo is off (fixes `passwd`)
  * Correctly set controlling TTY, makes `gpg` happy ([issue 30](https://code.google.com/p/hotwire-shell/issues/detail?id=30), [issue 65](https://code.google.com/p/hotwire-shell/issues/detail?id=65))
  * `Ctrl-s` starts search for File renderer
  * Fix **proc** on win32 (Suggested fix from tianxiaoji)

## Changes in Hotwire 0.620 ##

Visible Changes:

  * Change some system commands to open in new terminal window, which does not close when the command exits.  Examples include 'sudo' and 'su' - often you want to see the final output of the command after it exits.
  * Complete commands are only removed after they've been viewed (nice for background `make`, etc.)
  * Command output is significantly faster
  * Cache uid/gid lookups, which speeds up file listings
  * Basic preferences dialog
  * Menu mnemonics added
  * Support for turning off menu mnemonics, and using Emacs keybindings for input
  * Watch GConf for monospace font changes (if available)
  * Terminal supports Ctrl-click on URLs ([issue #55](https://code.google.com/p/hotwire-shell/issues/detail?id=#55))
  * Change window title based on tab name
  * New HotSshBuiltin (named **ssh**) which invokes hotssh (if available)
  * Add **kill** builtin, with completion on process list
  * Fix transparency of throbber
  * `term iotop` for `iotop` by default.

API Changes:

  * New API for registering completers for system commands: ShellCompleters

Notable bugfixes:

  * Ignore SIGHUP in subprocesses, because we close the pty when parent exits
  * Pass working directory onto programs run from menuitems ([issue #58](https://code.google.com/p/hotwire-shell/issues/detail?id=#58))

## Changes in Hotwire 0.600 ##

Hotwire now runs again at a basic level on Windows, though this is very much a work in progress.  See HotwireWindows.

Visible changes:

  * Basic input to system commands is now supported (press Ctrl-I)
  * Drag and drop works for files in FilePathRenderer (ls/cd)
  * Remove `SHIFT` keybinding for choosing completions; it was confusing
  * New **write** builtin writes pipelines to files (with -p option for pickling)
  * New **py** builtin allows running arbitrary Python code on current pipeline output ([issue 46](https://code.google.com/p/hotwire-shell/issues/detail?id=46))
  * New **current** builtin replaces **last**
  * Can start a pipeline with `| ` as a shortcut for `current | `.
  * New **sechash** builtin for creating secure hashes
  * New **mkdir** builtin, creates directories.
  * Improved internal Python interactive evaluator (now available in the menu)
  * Rebind Home/End to change input position; Control-Home/End now scroll output.
  * Right click menu on files gains "Move to trash" item.
  * Secondary tabs and new windows inherit default working directory from creating tab
  * Secondary tabs and new windows show **ls** as initial display
  * Command displays and terminal widgets can be turned into toplevel windows (Ctrl-Shift-N)
  * Can click on completions to choose them (future CompletionSystem2 will handle this better)
  * Reworked command header display to be cleaner
  * Terminal foreground and background colors may now be configured
  * Improved internal text editor with cancel dialog, better keybindings [Owen Taylor ](.md)
  * Default **term** more commands like `sudo`, `irssi`, `mutt`, `powertop`, `more`
  * `Escape` key at toplevel should grab input focus
  * **help** builtin shows available options
  * **proc** builtin defaults to showing your processes, new `-a` option for all

Notable bugfixes:

  * Support for gtksourceview2 in addition to gtksourceview
  * Add workaround for terminal sizing issues that mainly affected vi ([issue #35](https://code.google.com/p/hotwire-shell/issues/detail?id=#35))
  * Should run again without gnomevfs or GConf bindings on Unix (to help the OS X port)
  * Support cd to symbolic links to directories ([issue #20](https://code.google.com/p/hotwire-shell/issues/detail?id=#20)).
  * Fixed fallback application launching to work with xarchiver and other apps ([issue #34](https://code.google.com/p/hotwire-shell/issues/detail?id=#34))

Important other changes:

  * State (history and preferences) are now stored in a SQLite database.  This change should be transparent, but may impact usage on NFS for example, so is noted here.

## Changes in Hotwire 0.599 ##

Visible changes:

  * Menu items added.
  * New display UI for commands; there is an "overview" mode, and old commands don't always take up space.
  * Completed commands are now automatically removed 5 minutes after completion
  * Add basic support for user plugins in ~/.hotwire/plugins
  * Added builtin editor for when subprocesses invoke $EDITOR but the variable isn't set, because the default editor on most platforms requires a terminal.
  * Support for common-prefix completion; if you have several files named foo-x.c, foo-y.c, TAB will fill in from f to foo-.
  * Allocate a PTY when executing subprocesses; this forces them to be line-buffered so Hotwire gets output immediately.
  * Initial support for terminal codes (right now just backspace); this makes progress bars drawn by e.g. rpm work.
  * "ls" outputs filenames in locale order
  * Copy is now always Ctrl-C; Cancel is now Ctrl-Shift-C
  * Use monospace font for file renderer; this makes permissions column look nicer
  * File renderer now has a MIME type column
  * **cd** command is not undoable, since that was just confusing

Notable bugfixes:

  * Disable Ctrl-T/Ctrl-N keybindings when in terminal tab.
  * Avoid passing through Ctrl-shift-C to terminal (i.e. copy/paste won't interrupt subprocesses)
  * Correctly handle globs for non-current directories ([Issue #10](https://code.google.com/p/hotwire-shell/issues/detail?id=#10)).
  * Make first path item clickable ([issue #9](https://code.google.com/p/hotwire-shell/issues/detail?id=#9)).
  * Work on older PyGTK releases
  * Require exact matches for automatic command resolution (e.g. typing "foo RET" won't auto-expand to /usr/bin/foomatic)

## Changes in Hotwire 0.595 ##

Visible changes:

  * Ctrl-t now opens a new Hotwire tab
  * Ctrl-T (uppercase) now opens a terminal tab
  * **ps** builtin is now renamed **proc**.
  * When a terminal tab ends, if you have not switched tabs since its creation, the new selected tab will be the one from which the terminal tab was created.  In other words, "vi foo.c" works more smoothly.
  * The current directory selector is now a combo box of recent directories
  * The history view from the up arrow is now per-tab.  History search is still global.

Notable bugfixes:

  * Shell quotation should work better

## Changes in Hotwire 0.590 ##

Visible changes:

  * Better completion of executables in cwd (#83)
  * FilePath listing trims common prefix
  * FilePath listing includes owner/group/permissions
  * Tabs are reorderable via drag and drop (with new enough GTK+)

Notable bugfixes:

  * .desktop file references correct icon
  * Fix race condition in persistence framework (#81)
  * Correctly interrupt entire subprocess group with Cancel/Ctrl-C
  * Window resizing (#80)
  * Completion window should behave better (#88 and others)
  * Fix bold color in term (#85)
  * Start autoscrolling output again if scroll is at end
  * Tab close button draws correctly

## Changes in Hotwire 0.575 ##

Notable bugfixes:

  * Suck in Python 2.5's webbrowser.py so we work better on Python 2.4
  * Include hotwire icon
  * Don't lose on EPIPE from subprocesses
  * Ctrl-c cancel updates statusbar

## Changes in Hotwire 0.567 ##

Visible changes:

  * Support for creating new windows (in addition to new tabs)
  * Ctrl-c now Does The Right Thing; if you have a selection it copies, otherwise cancels last command
  * Tab switching is now Ctrl-# and not Alt-# to match gnome-terminal and Firefox (#74)
  * There is a basic menubar now for some discoverability
  * Alt-Left and Alt-Right keybindings are gone; I want to use these later for directory nav.  Use Ctrl-PageUp/PageDn or Ctrl-# instead.
  * Ctrl-Up and Ctrl-Down are convenient ways to cycle through previous command displays
  * The help display gains a link to the tutorial on the wiki
  * Wrap lines checkbox for unicode renderer (should this be persistent?)
  * `man` and `top` are now run with '''term''' by default

Notable bugfixes:

  * Headers in '''ls''' display work better (#76)
  * Shell command cancellation works much better now (pid was a global variable, oops!)
  * Some memory usage reduction fixes
  * Completion window hides itself appropriately in more situations now

## Changes in Hotwire 0.556 ##

  * Hotwire keeps track of "hot" working directories and offers them as completions when using 'cd'.
  * Completions now have icons (useful to distinguish real files from history completions)
  * New builtin 'fsearch' is like fgrep -R, but cooler.
  * New builtin 'prop' for accessing object properties
  * The completion window should flash a lot less during completion
  * Escape hides the completion window
  * Fix shell commands using [.md](.md) and {}
  * Terminal supports copy/paste with Ctrl-Shift-C, Ctrl-Shift-V.
  * Terminal uses system colors and monospace font
  * Terminal closes when command exits
  * Hotwire is now a singleton on Linux (support for new windows coming soon)

## Changes in Hotwire 0.554 ##

  * Native windows installer with no external dependencies on Python or GTK+.
  * Completion engine redone again.  You can now drill down into directories using SHIFT.
  * There is now interactive Firefox-style search over command output.  Try typing Ctrl-s.   Very handy for output of 'make'!
  * 'rm' and friends are implemented for Windows.
  * Default aliases (i.e. 'vi' -> 'term vi', 'ssh' -> 'term ssh').
  * Progress meters for 'rm' and friends.
  * On Linux, 'ls' now shows miniature pixbufs for files (like Nautilus)
  * On Windows, basic icons for files/directories work.
  * 'ls' now has size and last modified date
  * On Linux, 'ls' has right click menu to do 'Open with...', same list as Nautilus
  * 'ls' now requires '-a' to show hidden files
  * Completion window is fixed size so it doesn't go crazy on long commands; this one needs work still.
  * Cancelling shell subprocesses should be more reliable on Unix
  * 'cd' now only offers directories as completions (and infrastructure is there for other command-specific completions)
  * Executable completion handles current directory too (typing ./autogen.sh does the right thing)
  * Better code internally; it should be getting easier to port Hotwire to other platforms like BSD and Mac OS X.


---


Jump to: HotwireDevelopment