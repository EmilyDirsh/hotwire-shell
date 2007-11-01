import os,sys,platform

# set up our editor as default if none set
if 'EDITOR' not in os.environ:
    os.environ['EDITOR'] = 'hotwire-editor'

# Work around git bug
os.environ['GIT_PAGER'] = 'cat'

def is_windows():
    return platform.system() in ('Windows', 'Microsoft')

def is_unix():
    return platform.system() in ('Linux',)

def is_linux():
    return platform.system() == 'Linux'

# These files are the right place to do global, platform-specific early
# initialization and share code between different components in this tree.
if is_unix():
    import hotwire.sysdep.unix
elif is_windows():
    import hotwire.sysdep.win32
    
def do_late_init():
    if is_unix():
        import hotwire.sysdep.unix_lateinit
    elif is_windows:
        import hotwire.sysdep.win32_lateinit

