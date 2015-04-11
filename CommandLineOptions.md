_Eventually this may form the basis of a man page_

# Hotwire command line options #

**Synopsis** ` hotwire [-dhnu] [dir-path] `

| Short Form | Long Form | Meaning |
|:-----------|:----------|:--------|
| -d | --debug | Set the debug flag for extra output |
| -h | --help | show usage and exit |
| -n | --no-persist | New instance of Hotwire, useful for testing new code. |
| -u | --unsaved | Don't save commands to history |

After these commands, you can put in the path to a directory.  Hotwire will start in that directory.  It defaults to your home directory.

For more advanced debug options, please look at the source code in [ui/hotwire](http://code.google.com/p/hotwire-shell/source/browse/trunk/ui/hotwire)

# Hotssh command line options #