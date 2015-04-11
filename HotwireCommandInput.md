# Why doesn't my command work? #

Hotwire is not fully command-compatible with a traditional Unix terminal+shell; for more background on this see HotwireVsBinSh.

# How do I make it work? #

If the command requires simple text input, type `Ctrl-I`.  This is sufficient for applications such as the `mysql` and `python` shells.

For real terminal applications (e.g. `top`, `vi`), you can type `term top`.  Hotwire has a [default list](http://hotwire-shell.googlecode.com/svn/trunk/hotwire/sysdep/unix_lateinit.py) of terminal applications internally - if your application is public, please file an issue to get it added to this list.

Another alternative is to use a real GUI version of the command.  `nemiver` instead of `gdb`, for example.