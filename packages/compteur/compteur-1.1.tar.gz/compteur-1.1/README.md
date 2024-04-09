# Compteur

I use Python scripts in crontab. Sometimes, a script crashes, and I receive an email with the error.  
But it can be a random crash and I do not need to know it, as it will not crash next time the script is launched.

Goal of this package is to track how many times an error occurs. I can define a limit of # errors before warning me.

## Exemple

```python
#!/usr/bin/env python3
from compteur import Compteur

cpt = Compteur('smartname')

try:
    # My wonderful script
except:
    cpt.inc()
    if cpt.isLimit():
        raise
else:
    cpt.reset()
finally:
    # do something
```