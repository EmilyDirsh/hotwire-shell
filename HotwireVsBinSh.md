Hotwire is not a terminal emulator, nor is it something you can set as your Unix "login shell"; instead, Hotwire unifies the concepts of shell and terminal and can natively do about 80-90% of what one would normally do in a terminal+shell; for the rest, Hotwire can embed VTE.

# Modern interface #

The "not a terminal" aspect of Hotwire is very important to understand.  Hotwire is not fully compatible with the concept of a traditional Unix shell and terminal.  First, the command language is different (see HotwireScripting).  While Hotwire does support globs, the pipeline system is object oriented (HotwireArchitecture); but other aspects such as environment variables, `for` loops etc. are not supported at this time.  However, you can do extended scripting in the full Python language using the **py** builtin.


Second, the default system command display is not a full terminal emulator.  But in real world usage today, there are very few applications that actually require a real terminal emulator.  What Hotwire does is to simply [make a list](http://hotwire-shell.googlecode.com/svn/trunk/hotwire/sysdep/unix_lateinit.py) of them, and run them in something that is a real Unix terminal emulator - a [VTE window](http://developer.gnome.org/arch/gnome/widgets/vte.html).  It is likely in a future release Hotwire will have automatic handling of legacy terminal apps - see FutureFeaturesWhiteboard.

So Hotwire treats terminal applications specially, but the vast majority of traditional Unix commands generally output human-readable text, occasionally taking a line of input.  Think `make`, `dmesg`, `cat`, `tg-admin quickstart`, etc.  Hotwire makes all system commands asynchronous, and output is shown in individual windows.  Even if you execute **ls** on a big directory or **cat** on a big file, you can keep typing other commands\ without hitting `^Z;bg`.  There is never any problem with the output from different background commands being intermixed.

The entire output of every command is saved by default.  This is useful for things like _make_.  Also, command output is searchable Firefox-style.

# Desktop integration #

One major goal of Hotwire was to significantly improve the default experience of a command shell by integrating with the windowing system and desktop environment.

For example, Hotwire integrates with the platform's preferred application framework, file thumbnailing, etc.

# Designed to be a better interactive shell #

Hotwire has builtins that are similar to many Unix commands, but have better defaults and are more oriented for interactive use.

  * **rm** moves files to `~/.Trash` (on Unix), `Recycle Bin` on Windows; also does not distinguish between removing directories and files (no `-r` option needed).
  * **cd** automatically lists the contents of the directory you change to
  * **ls** links are clickable (view file, cd to directory); also right-click gives you file manager option menu
  * **filter** (analogous to Unix _grep_) shows what text matched in bold, and can filter objects too
  * **proc** process list has right-click menu to kill, is not just big glob of text

# Also working towards improving the scripting experience #

Because Hotwire is written in pure Python, it is also extensible using the same language - which has futuristic programming features like arrays.   There is also some initial research on making Python closer to a system scripting language; see HotwireScripting.


---

See other RelatedProjectsAndIdeas.