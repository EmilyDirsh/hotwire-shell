# Project Ideas #

The intent of this page is to be a whiteboard for potential Hotwire improvements that are not yet baked enough to turn into issues.

## HotwireScripting ##

We need to formalize the current Hotwire pipeline language.  See HotwireScripting for the page on this.

## IronPython ##

Would be interesting to try rewriting Hotwire to run on IronPython+Gtk#+Mono rather than CPython+pygtk.  The main motivation for this is to get **real threads**.  We need this in order to be able to execute arbitrary user code without blocking the UI.

## CompletionSystem2 ##

See [CompletionSystem2](CompletionSystem2.md).

## 100% Terminal Compat ##

Possible idea for killing the hardcoded list of tty apps - if in the initial stream load, we see stuff that looks like terminal codes (which almost certainly isn't valid UTF-8), we create a new VTE window and push that data into it.  This might not even be that hard.  Just use [vte\_terminal\_set\_pty](http://library.gnome.org/devel/vte/unstable/VteTerminal.html#vte-terminal-set-pty)?

## Extend builtin list ##

More ideas for object yielding builtins:

  * query installed packages with packagekit?
  * query open windows