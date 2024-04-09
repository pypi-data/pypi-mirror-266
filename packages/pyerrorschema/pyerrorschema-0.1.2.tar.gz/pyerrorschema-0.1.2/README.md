# PyErrorSchema

## Installation

The source code is currently hosted on GitHub at [here](https://github.com/sodinfeliz/PyErrorSchema).

Binary installers for the latest released version are available at the [Python Package Index (PyPI)](https://pypi.org/project/pyerrorschema/).

```sh
pip install pyerrorschema
```

## Examples

```python
from pyerrorschema import FastAPIErrorSchema

# Creating a error schema
err = FastAPIErrorSchema.database_error(
    loc=["request", "body"],
    input={'data_path': 'test'},
)

# Converting the error to a dictionary and printing it
print(err.to_dict())
```

This will output:

```txt
{'type': 'database_error', 'msg': 'Database operation failed.', 'loc': ['request', 'body'], 'input': {'data_path': 'test'}}
```
