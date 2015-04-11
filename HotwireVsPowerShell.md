Hotwire steals PowerShell's idea of pipelining objects, not byte streams (HotwireArchitecture).

However, that's about where the similarities end.  Some important differences:

  * Hotwire is not interested in becoming a full-fledged scripting language, especially not one with lots of "${}.%".  See HotwireScripting.
  * Hotwire aims for a much richer default user experience.  There are the obvious things like using icons and having clickable links, but besides that Hotwire's client requires a window system and a canvas; commands and renderers can assume they exist.

## Related threads ##

[Ars Technica discussion on Powershell](http://episteme.arstechnica.com/eve/forums/a/tpc/f/12009443/m/128001068831/p/1)