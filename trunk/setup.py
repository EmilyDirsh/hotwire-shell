# This file is part of the Hotwire Shell user interface.
#   
# Copyright (C) 2007 Colin Walters <walters@verbum.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import os,sys
from distutils.core import setup

if __name__ == '__main__' and hasattr(sys.modules['__main__'], '__file__'):
    basedir = os.path.dirname(os.path.abspath(__file__))
    up_basedir = os.path.dirname(basedir)
    if os.path.basename(basedir) == 'hotwire-shell':
        print "Running uninstalled, extending path"
        sys.path.insert(0, basedir)
        os.environ['PYTHONPATH'] = os.pathsep.join(sys.path)
from hotwire.version import __version__

def svn_info(wd):
    import subprocess,StringIO
    tip = {}
    for line in StringIO.StringIO(subprocess.Popen(['svn', 'info', wd], stdout=subprocess.PIPE).communicate()[0]):
        line = line.strip()
        if not line:
            continue
        (k,v) = line.split(':', 1)
        tip[k.strip()] = v.strip()
    return tip

def svn_dist():
    import subprocess,tempfile
    import shutil

    dt = os.path.join('dist', 'test')
    try:
        os.mkdir('dist')
    except OSError, e:
        pass
    if os.path.exists(dt):
        shutil.rmtree(dt)
    subprocess.call(['svn', 'export', '.', dt])
    oldwd = os.getcwd()
    os.chdir(dt)
    verfile = open(os.path.join('hotwire', 'version.py'), 'a')
    verfile.write('\n\n##AUTOGENERATED by setup.py##\nsvn_version_info = %s\n' % (repr(svn_info(oldwd)),))
    verfile.close()
    subprocess.call(['python', 'setup.py', 'sdist', '-k', '--format=zip'])

def svn_dist_test():
    import subprocess
    svn_dist()
    os.chdir('hotwire-' + __version__)
    subprocess.call(['python', os.path.join('ui', 'test-hotwire')])

if 'svn-dist' in sys.argv:
    svn_dist()
    sys.exit(0)
elif 'svn-dist-test' in sys.argv:
    svn_dist_test()
    sys.exit(0)

kwargs = {}

if 'py2exe' in sys.argv:
    import py2exe
    kwargs['windows'] = [{'script': 'ui/hotwire', #'icon_resources': [(1, 'hotwire.ico')]
                        }]
    kwargs['options'] = {'py2exe': {'packages': 'encodings',
                                    'includes': 'cairo, pango, pangocairo, atk, gobject'}
                         }
else:
    kwargs['scripts'] = ['ui/hotwire', 'ui/hotwire-editor']
    kwargs['data_files'] = [('share/applications', ['hotwire.desktop']), 
                            ('share/icons/hicolor/24x24/apps', ['images/hotwire.png']),
                            ('share/icons/hicolor/22x22/apps', ['images/hotwire-22.png']),
                            ('share/hotwire/images', ['images/throbber.gif', 'images/throbber-done.gif'])]
    from DistUtilsExtra.command import *    
    kwargs['cmdclass'] = { "build_extra" : build_extra.build_extra,
                           "build_i18n" :  build_i18n.build_i18n,
                           "build_help" :  build_help.build_help,
                           "build_icons" :  build_icons.build_icons }    

setup(name='hotwire',
      version=__version__,
      description='Hotwire Shell',
      author='Colin Walters',
      author_email='walters@verbum.org',
      url='http://hotwire-shell.org',
      packages=['hotwire', 'hotwire_ui', 'hotwire_ui.renderers', 'hotwire.builtins',
                'hotwire.pycompat', 'hotwire.sysdep', 'hotwire.sysdep.fs_impl', 
                'hotwire.sysdep.proc_impl',
                'hotwire.sysdep.term_impl', 'hotwire.sysdep.ipc_impl',
                'hotvte', 
                'hotapps', 'hotapps.hotssh'],
      **kwargs)

