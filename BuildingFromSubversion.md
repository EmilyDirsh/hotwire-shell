# Dependencies #

Hotwire requires [Python >= 2.4](http://python.org), [PyGTK](http://pygtk.org) at a minimum.

## Linux/Unix ##
On Unix systems you will want your operating system's packages of the Python bindings for `gconf`, `gnomevfs`, `vte`, `dbus`, `gtksourceview`, though Hotwire should work (with reduced functionality) without them.

### Fedora 7/8 ###
```
yum install gnome-python2-gnomevfs python-dbus gnome-python2-desktop gnome-python2-gconf  vte pygtksourceview
```

### Debian/Ubuntu ###

```
apt-get install python-vte python-dbus python-gnome2 python-pygtksourceview
```

## Windows and MacOS X ##

See HotwireWindows and [HotwireMacOSX](HotwireMacOSX.md) respectively.

# Source Code Using Subversion #

```
svn checkout http://hotwire-shell.googlecode.com/svn/trunk/ hotwire
```

See [Source page](http://code.google.com/p/hotwire-shell/source) for more information on checking out the code, and [SVNBook](http://svnbook.red-bean.com/en/1.1/ch03s05.html) for information about working with a Subversion source tree.

# Source Code Using Git #

The Hotwire author has found [git-svn](http://www.kernel.org/pub/software/scm/git/docs/git-svn.html) to be extremely useful for doing Hotwire development using [Git](http://git.or.cz/), but maintaining the canonical source in SVN.

# Running Hotwire from source #

Run this command from the source tree after having checked out from Subversion or unpacking the Zip file:

```
python ui/hotwire
```

That's it!  There is no compilation process, everything should work uninstalled.

## Using Hotwire to hack Hotwire ##

Use the ''-n'' option to tell Hotwire to create a new instance:

```
python ui/hotwire -n
```

## Creating a GNOME panel launcher ##

If you want to run Hotwire from your Subversion checkout, the best thing to do is to create a GNOME Panel launcher for it (or equivalent for other desktop environment).  Here are some instructions for GNOME:

  * Right click on the panel, select **Add to Panel**.  Choose **Custom Application Launcher**.  In the **Name** field, put `Hotwire`.  In the **Command** field, put `python /path/to/hotwire/ui/hotwire`.  Change `/path/to/hotwire` to the name of your Hotwire checkout directory.  You should now be able to click on it to launch Hotwire uninstalled.

# What to hack on? #

[ExtendingHotwire](ExtendingHotwire.md) explains how to create an extension in your home directory.  To modify the core, you might look at issues tagged with "HotwireLoveBug" for a bug that a new developer could start on.

See also [RoadMap](RoadMap.md) for some longer-term projects.