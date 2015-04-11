# Status #

Hotwire should generally work on KDE - though you will want to be sure you have the Python GnomeVFS bindings installed at least.  There are a few areas in which we could integrate better - patches for this would be happily accepted, or even just pointers on how to do it.

# What not to do #

Another UI written in Qt isn't that interesting; would be a significant amount of work for almost no real benefit. [Gtk-Qt](http://www.freedesktop.org/wiki/Software/gtk-qt) is a better approach for visual integration. But there are definitely other useful things we can do to be a better KDE experience:

# Preferred applications #

Would be nice to pick up a KDE user's preferred text editor, for example.  [KTrader](http://api.kde.org/3.5-api/kdelibs-apidocs/kio/kio/html/classKTrader.html#f317c76b7cfb2a1e8ccc0df72676b2d5) looks like the way to do this.

# KDE icons #

Should use the KDE file thumbnailer.

# File dialogs #

Right now we don't have any file selectors, so this is moot.

# Others? #

Add comments with your suggestions.