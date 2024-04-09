"""
Example
=======
```shell
$ python -m micropype mymodule.submodule.function1 --x 0.2 --y 12 --config myconfig_file.json --db.path /path/to/the/db.sqlite

```

"""
import sys
from micropype.commandline import run_function_from_commandline

r = run_function_from_commandline(*sys.argv[1:])
if r is not None:
    print(r)
