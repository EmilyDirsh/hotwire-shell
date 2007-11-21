import os, pwd, grp

os.environ['HOTWIRE_SHELL'] = '1'

# Ensure subprocesses don't try to treat us as a full tty
os.environ['TERM'] = 'dumb'
# Fix Fedora and probably other systems
standard_admin_paths = ['/sbin', '/usr/sbin']
path_elts = os.environ['PATH'].split(':')  
path_fixed = False
for path in standard_admin_paths:
    if not path in path_elts:
        path_fixed = True
        path_elts.append(path)
if path_fixed:
    os.environ['PATH'] = ':'.join(path_elts)

# set up our editor as default if none set
if 'EDITOR' not in os.environ:
    os.environ['EDITOR'] = 'hotwire-editor'

# Work around git bug
os.environ['GIT_PAGER'] = 'cat'

# This is stupid; Unix should just do this.
_pwuid_cache = {}
def getpwuid_cached(uid):
    try:
        return _pwuid_cache[uid]
    except KeyError, e:
        _pwuid_cache[uid] = result = pwd.getpwuid(uid)
        return result

_grgid_cache = {}
def getgrgid_cached(gid):
    try:
        return _grgid_cache[gid]
    except KeyError, e:
        _grgid_cache[gid] = result = grp.getgrgid(gid)
        return result
