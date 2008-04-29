# This file is part of the Hotwire Shell user interface.
#   
# Copyright (C) 2007,2008 Colin Walters <walters@verbum.org>
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

import os,sys,subprocess
from distutils.core import setup
from distutils.command.install import install

APPNAME = 'hotwire-ssh'
MODDIR = 'hotssh'

if __name__ == '__main__' and hasattr(sys.modules['__main__'], '__file__'):
    basedir = os.path.dirname(os.path.abspath(__file__))
    up_basedir = os.path.dirname(basedir)
    if os.path.basename(basedir) == APPNAME:
        print "Running uninstalled, extending path"
        sys.path.insert(0, basedir)
        os.environ['PYTHONPATH'] = os.pathsep.join(sys.path)
__import__(MODDIR + '.version', fromlist=['__version__'])

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
    verfile = open(os.path.join(MODDIR, 'version.py'), 'a')
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
    # FIXME no test suite, below does not work
    svn_dist_test()
    sys.exit(0)

kwargs = {}

if 'py2exe' in sys.argv:
    import py2exe
    # FIXME doesn't work on windows
    kwargs['windows'] = [{'script': 'ui/hotwire', #'icon_resources': [(1, 'hotwire.ico')]
                        }]
    kwargs['options'] = {'py2exe': {'packages': 'encodings',
                                    'includes': 'cairo, pango, pangocairo, atk, gobject'}
                         }
else:
    kwargs['scripts'] = ['bin/hotssh']
    kwargs['data_files'] = [('share/applications', ['hotssh.desktop']), 
                            ('share/icons/hicolor/24x24/apps', ['images/hotwire-openssh.png']),
                           ]
    from DistUtilsExtra.command import *
    kwargs['cmdclass'] = { "build_extra" : build_extra.build_extra,
                           "build_i18n" :  build_i18n.build_i18n,
                           "build_help" :  build_help.build_help,
                           "build_icons" :  build_icons.build_icons }
    
class HotInstall(install):
    def run(self):
        install.run(self)
        if os.name == 'posix':                       
            if self.root is None:
                print "Running gtk-update-icon-cache"
                subprocess.call(['gtk-update-icon-cache', os.path.join(self.install_data, 'icons')])
kwargs['cmdclass']['install'] = HotInstall                    

setup(name=APPNAME,
      version=__version__,
      description='Hotwire SSH',
      author='Colin Walters',
      author_email='walters@verbum.org',
      url='http://hotwire-shell.org',   
      packages=['hotssh', 'hotvte'],
      **kwargs)
