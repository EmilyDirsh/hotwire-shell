# THIS PAGE IS OBSOLETE #

See HotwireScripting.

# Old content preserved for historical reference #

If you want to write multi-line scripts with variables, flow control, data structures etc., **write them in Python**.

It may make sense to import Hotwire's command pipeline code for parts of a Python program:

```
from hotwire.command import Pipeline

p = Pipeline.parse('ps | filter java cmd')
p.execute()
for result in p.get_output():
  result.kill()
```

But this is not really a focus for development.