The Windows port has basic functionality in the 0.600 release; however there is much to do.  It could use a good Windows Python hacker, especially one knowledgable in PyGTK, to help bring it up to par.  When we feel Hotwire is a "good enough" experience on Windows, there will be official binaries.

There are a number of issues such as incomplete path adjustments (see below), as well as
missing system integration work such as file icons, application launching, using Recycle Bin, etc.

If you're interested in trying Hotwire on Windows, you can download an integrated Windows binary (see http://code.google.com/p/hotwire-shell/downloads/list?can=1).  However, it is more recommended to follow the instructions below so that you can hack on Hotwire itself.

# Being a shell on Windows #

One key thing to understand is that on Windows, Hotwire always uses forward slashes (/) as directory separators, not backslashes (\).  This resolves a conflict between the backslash as directory separator, and Hotwire's use of it as a quotation mechanism.

To implement this, there are special path manipulation functions in `hotwire/fs.py` which you must generally use in all crossplatform Hotwire code.

# Getting a development environment setup #

## Python Downloads ##

  * [[Python](http://python.org/download/)].  Get the MSI.
  * [[Python Win32 Extensions](http://python.net/crew/mhammond/win32/Downloads.html)].  Follow the link to Sourceforge.  You need to match the extension installer version to your Python version; at the time of this writing current Python is 2.5, so you'd download '''pywin32-210.win32-py2.5.exe'''.

## PyGTK ##

There are a few choices here; I used the [[PyGTK FAQ](http://faq.pygtk.org/index.py?req=show&file=faq21.001.htp)] instructions, but
there is work on a [[new PyGTK installer](http://aruiz.typepad.com/siliconisland/2007/05/tango_and_gtk_l.html)].

You can initially run Hotwire from cmd.exe or powershell.exe as you choose.  I use
[Emacs](ftp://ftp.gnu.org/gnu/emacs/windows/) for development, but of course there are hundreds of other choices.
Here's my setup for Powershell:

```
$env:path += ';C:\Python25'
cd My Documents\hotwire
python ui/hotwire
```

# Running Hotwire from source #

These instructions are largely the same as HotwireDevelopment.

# Building an installer #

Just now got [[Py2exe](http://www.py2exe.org/)] to work.  In particular see [[Py2exe PyGTK page](http://www.py2exe.org/index.cgi/Py2exeAndPyGTK)].

## Initial setup ##

```
mkdir dist
```

Copy the `lib` and `etc` directories from `C:\Program Files\Common Files\GTK\2.0` into the new `dist` directory.

## Running py2exe ##

```
python setup.py py2exe
```


---


See also: HotwireDevelopment