# Short term (next year) #

Besides bugfixes, these are the areas which are feasible for 2008:

### Remoting ###

See [Remoting](Remoting.md).

### Better UI ###

~~We could really do with a UI cleanup, looks do matter~~.  This one is mostly done, see [issue 153](https://code.google.com/p/hotwire-shell/issues/detail?id=153).

### Porting ###

To truly be a shell, we need to work on better crossplatform support.  See [HotwireWindows](HotwireWindows.md) and [HotwireMacOSX](HotwireMacOSX.md).

### Website ###

It'd be nice to have integrated support for extensions similar to `addons.mozilla.org`, and pastebin type functionality.

### 100% Unix Terminal Compatibility ###

This one seems possible - what we could do is have a proxy which detects ANSI terminal codes and spawns a real terminal.  This does get into some design-type questions though about whether we set TERM=dumb or not.

### IDE/Editor integration ###

A shell is a natural companion to many developers using IDEs or plain editors.  There's plenty of integration opportunities that weren't really possible with a traditional Unix shell, such as having a shell window bound to a project, etc.

### Improved scripting ###

We should support multi-line scripts better.  Think "Tomboy of code".  [Issue 79](https://code.google.com/p/hotwire-shell/issues/detail?id=79) is related.

# Medium term (2-3 years) #

### Multi-language runtime base ###

To properly support multiple languages, we need to use a better runtime than CPython.  There are realistically only two choices here.  OpenJDK+Jython, or Mono+IronPython. Then if we want to support say Ruby, we can mix in JRuby or IronRuby.

We should carefully pay attention to the progress of these projects and evaluate which one it makes sense to choose as a base.