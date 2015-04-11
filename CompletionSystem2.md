# Need for a new system #

The current system has a number of flaws.

  * It only shows you at most 4 matches, and wastes a lot of horizontal space.
  * You can't click on items to choose.
  * It's constantly trying to complete, but you may want to see what's underneath it.
  * There is no way to have it use more space for when you do want that.

# Completion2 mockups #

Initially, completions will be a single line multi-column display.  This will
make them relatively unobtrusive.  You know how many there are, but don't see a big list.  You can continue to refine the list by typing.  It will update on a timeout (we might want to have a status message for when the completions are stale).

![http://hotwire-shell.googlecode.com/svn/screenshots/Hotwire-Completion2-1.png](http://hotwire-shell.googlecode.com/svn/screenshots/Hotwire-Completion2-1.png)

Now, when you hit TAB - if there is only one completion, we choose it.  If all completions have a common prefix, we fill in with that, and recomplete.  This matches `bash`.  If there are ambiguous completions, `TAB` expands the display:

![http://hotwire-shell.googlecode.com/svn/screenshots/Hotwire-Completion2-2.png](http://hotwire-shell.googlecode.com/svn/screenshots/Hotwire-Completion2-2.png)

See also [issue 14](https://code.google.com/p/hotwire-shell/issues/detail?id=14).  We need a canvas/table layout for this.

Should completions be case-insensitive?  See [issue 61](https://code.google.com/p/hotwire-shell/issues/detail?id=61).

# Thoughts on code changes #

## Completion objects ##

Completions match the start of input tokens.

```
class Completion(object):
  token, info, icon
```

The `token` represents what we have to add to the current input to get a valid completion.  It is unique among a set of returned completions - this differs from the current system which will return both the **ls** builtin and `/bin/ls` for "ls".  `info` is an arbitrary string describing additional data (for example, it might be "Builtin" for a builtin, or "/usr/bin/foo" for a system executable completion, or "python -c ..." for a process ID completion).

Now, we need to rewrite the current `hotwire/completion.py` classes to generate these types of completions.  This should be a fairly large simplification.

## Rework keyboard handling + display ##

Try to move things out of shell.py if we can into ui/completion.py.  Generally follow mockups above.