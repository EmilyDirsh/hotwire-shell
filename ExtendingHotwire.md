# Extending Hotwire with custom Python #

Hotwire's extension support is fairly basic right now; essentially, it allows you to place arbitrary Python code in a file (ending in `.py`) in `~/.hotwire/plugins/`.

# Adding environment variables #

Create a file, e.g.: `~/.hotwire/plugins/myenv.py`.

```
import os
os.environ['JAVA_HOME'] = '/usr/java/jdk1.5.0_13'
```

Then in Hotwire:

```
py-eval -f ~/.hotwire/plugins/myenv.py
```

# Creating an alias #

```
from hotwire.cmdalias import AliasRegistry
# If you want your alias to expand to a system command, you must specify sys
AliasRegistry.getInstance().insert('make', 'sys make -j 3')
AliasRegistry.getInstance().insert('la', 'ls -a')
```

# Adding a new builtin #

You can also create and register new builtins.  Looking at existing ones such as [LsBuiltin (ls)](http://hotwire-shell.googlecode.com/svn/trunk/hotwire/builtins/ls.py) is a good way to learn by example. You can also look at existing ExternalPlugins .

Also, below is a heavily-commented sample file called `fruit.py` which demonstrates many of Hotwire's current extension points:

```
## A sample Hotwire extension showing how to create new objects, builtins,
## renderers, and completers.

import os, sys, stat

import gtk

from hotwire.builtin import Builtin, BuiltinRegistry
from hotwire.completion import Completion,Completer
from hotwire_ui.render import ClassRendererMapping, TreeObjectsRenderer, menuitem

## This is an arbitrary Python object we define here.  It has no dependency or
## relation to Hotwire - your builtin may reuse an object from the Python system
## library, or one that already exists in the Hotwire core (like FilePath).
class Fruit(object):
  flavor = property(lambda self: self._flavor)
  def __init__(self, flavor):
    ## Our object has a single property, named "flavor".
    self._flavor = flavor

## You can fairly easily subclass your own objects from Completer.  Here 
## is one which completes two values.  For more completion samples,
## see hotwire/completion.py in the source tree.
class FruitCompleter(Completer):
  def __init__(self):
    super(FruitCompleter, self).__init__()

  def completions(self, text, cwd, **kwargs):
    for name in ['apple', 'orange']:
      if name.startswith(text):
        yield Completion(name[len(text):], Fruit(name), name)

## A Builtin is the Hotwire term for a Python command.  Here is one which constructs
## fruit objects based on the strings passed to it (note the completer above yielded
## strings, not objects).
## For more about builtins, see hotwire/builtin.py.
class FruitBuiltin(Builtin):
  """A demo builtin that shows you fruit."""
  def __init__(self):
    super(FruitBuiltin, self).__init__('fruit',
                                       ## The output argument is very important; it
                                       ## tells Hotwire what type of object your
                                       ## builtin outputs.
                                       output=Fruit,
                                       ## This argument tells Hotwire our command doesn't
                                       ## have any side effects, which will be useful later
                                       ## when more commands implement undo.
                                       idempotent=True)

  ## We override get_completer to tell Hotwire to use our FruitCompleter.
  def get_completer(self, context, args, i):
    return FruitCompleter()

  ## The execute method gets a "context" object which has attributes such as "cwd" for
  ## the current working directory, "input" for an iterable queue of the input side of
  ## the pipeline, and more (see hotwire/command.py).  
  def execute(self, context, args):
    for flavor in args:
      ## Notice that Hotwire builtins are normally generators (http://www.python.org/dev/peps/pep-0255/).
      yield Fruit(flavor)

## You must call this function to tell Hotwire about your builtin class.  Note that all
## builtins are singletons - you can easily store per-execution state as local variables,
## and the "context" object has an "attribs" dictionary which may also be convenient.
BuiltinRegistry.getInstance().register_user(FruitBuiltin())

## We need to tell Hotwire how to display objects of class Fruit.  In the future,
## Hotwire will gain a more intelligent default renderer which will allow you to explore
## properties, etc.  This renderer subclasses TreeObjectsRenderer which is GtkTreeView
## based.
class FruitRenderer(TreeObjectsRenderer):
    def _setup_view_columns(self):
        ## This single line tells Hotwire to add a column with a title "Flavor", displaying
        ## the "flavor" attribute of the Fruit objects.
        self._insert_propcol('flavor', title='Flavor', ellipsize=False)

    ## This decorator tells Hotwire to create a right-click menu item with that name.
    @menuitem()
    def eat(self, iter):
        fruit = self._model.get_value(iter, 0)
        dlg = gtk.MessageDialog(message_format='You ate %s!' % (fruit.flavor,))
        dlg.run()

## Finally, tell Hotwire to use our FruitRenderer for objects of type Fruit.
ClassRendererMapping.getInstance().register(Fruit, FruitRenderer)

```

To play with this, save it to `~/.hotwire/plugins/fruit.py`.  You can load it at runtime with `py-eval -f ~/.hotwire/plugins/fruit.py`, or restart Hotwire.

Future plans include a Firefox-style extension mechanism.

That's it for now; for hacking Hotwire further, you should probably just get a checkout out of the source tree and dive into HotwireDevelopment.