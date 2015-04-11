Because Hotwire is currently written entirely in Python, we generally follow the
[Python style](http://www.python.org/dev/peps/pep-0008/) guidelines.

Specific style choices made here:

  * Use 4 spaces for indentation; no tabs
  * Always subclass from `object` or `gobject.GObject`
  * Initialize **all** object members in the `__init__` constructor, or in functions called directly from it.
  * Use the `_` prefix for "protected" members, and the `__` prefix for private members.
  * For important properties, use the `property` mechanism and add a docstring.
  * Files which `import gtk` (generallly `hotwire_ui` and `hotapps`) should be GPL, others are MIT.

Overall architecture:

  * Never call functions which can block on I/O from the main thread.  Instead, create a worker thread and use `gobject.idle_add` to communicate results to the main loop.
  * The only hard dependencies are Python 2.4, and GTK+ 2.8.  However - please do try to integrate with the rest of the system (using the platform's file thumbnailing API, notification system, etc.) by adding optional code.  For example, you can add a new method to an interface in `sysdep`, and implement it for your platform.