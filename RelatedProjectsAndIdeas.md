# Core inspirations #

HotwireVsBinSh talks about what Hotwire takes from Unix `````/bin/sh````` (a lot)

HotwireVsPowerShell is dedicated to the Hotwire's influence from Windows PowerShell (mostly object piping).

# Other projects #

[Gnome Command Interface](http://www.stanford.edu/~dramage/gci/) - GCI has some similarites (Python, GNOME
basis, backgrounding jobs).  However, a big push GCI seems to be implementing strongly reliable completion, with a lot of work
on grammar.  In contrast Hotwire has a simpler completion scheme (basically just like Unix shell, assuming
file names).  Hotwire's syntax is ridiculously simple:  `pipeline.split(" | ")`  Other differences are
Hotwire's interest in being crossplatform.

[XMLTerm](http://web.archive.org/web/20050207072807/xmlterm.sourceforge.net/) - Old, but highly innovative for the time.

[Terminator](http://software.jessies.org/terminator/) - A terminal with a few added features like find and unlimited scrollback by default.

[CUI](http://linux.pte.hu/~pipas/CUI/) - Looks based around having parsers for the output
of various shell commands, and doing things like colorization, linkification of file names, etc.  Related, but I think
the approach (C, parsing shell commands instead of implementing them natively) is going to be too restrictive.
Hotwire tries to implement a lot of useful functionality inside the core (fixing it along the way, e.g. `rm`),
but still allowing callouts to `/bin/sh`.

[SCSH](http://www.scsh.net/resources/commander-s.html) - Scheme and ncurses based enhanced interactive shell, very interesting ideas in there - see the PDF.

[Anthias](http://anthias.sourceforge.net/) A multi-terminal with integrated file browser; does not have object pipeline. Targets KDE, written in C++.  They chose to
do a frontend/backend separation from the start using a custom protocol.  Development looks stalled.

[RubyUnix](http://rubyunix.rubyforge.org/) - Rewrite a traditional Unix shell in Ruby (the goal looks more like IPython than Hotwire)

[PyShell](http://pyshell.sourceforge.net/) - Rewrite traditional Unix shell in Python.

[Omnitty SSH](http://omnitty.sourceforge.net/) - Multiplex commands over multiple hosts

[gsh](http://personal.atl.bellsouth.net/v/c/vcato/gsh/) Very similar ideas to Hotwire. Fairly old. Written in TCL/TK.  TODO: Download source and investigate this more.

[Wicked Shell](http://www.wickedshell.net/) - Shell integration for Eclipse.  Looks like they have some basic
completion and crossplatform functionality.  Might be worth investigating.

[LinuXML](http://www.geocities.com/ResearchTriangle/Forum/6751/) Looks like they picked a Big Idea (XML), rather than trying to be practical.

[vshnu](http://www.cs.indiana.edu/~kinzler/vshnu/) Attempt at tty-based shell in Perl. Quite old now but may have some ideas.

[Fish shell](http://www.fishshell.org/) - Interested in fixing some of the same problems we are (e.g. features not on by default), although they
are limited by their choice of being just a login shell instead of combination "terminal"+shell.

[Viewglob](http://viewglob.sourceforge.net/) - Does some functional (but ugly) filemanager/terminal integration

[IPython](http://ipython.scipy.org/) - Looks like you can execute system commands, but more oriented towards
being a tool for Python programming.  Still though a pretty big project with some interesting ideas and
probably code.  Might want to look at their "distributed computing" stuff - maybe a better way to run pipelines?  **Update**: [IPipe](http://ipython.scipy.org/moin/UsingIPipe) looks interesting

[osh](http://geophile.com/osh/) - Pipes objects.  May be interesting for syntax ideas?

[EShell](http://www.emacswiki.org/cgi-bin/emacs/CategoryEshell) - Highly programmable with Emacs Lisp, targets Emacs UI.  Also worth pulling ideas from.

[Sun Shared Shell](http://www.sun.com/service/sharedshell/userguide.jsp) - is shared interesting for us?

[Quasi](http://quasi-shell.sourceforge.net/) - no GUI, seems to have syntax ideas

[KHPython](http://www.boddie.org.uk/david/Projects/Python/KDE/khpython/index.html) - Python worksheet program

[Pash](http://pash.sourceforge.net/) is a cross platform version of [Microsoft Powershell](http://en.wikipedia.org/wiki/Windows_PowerShell) that runs on the [Mono](http://www.mono-project.com/Main_Page) runtime as well as standard .NET

# Articles #

[CLI](http://polylithic.net/cli/) - Website devoted to the CLI.

[Advogato entry](http://www.advogato.org/article/242.html) - Someone wondering why the Unix shell isn't better.

[Free Software Magazine](http://www.freesoftwaremagazine.com/columns/why_cant_free_software_guis_be_empowering_instead_limiting) has an article asking "If CLIs are so impenetrable, why don’t we use some GUI technology to make them less so?"