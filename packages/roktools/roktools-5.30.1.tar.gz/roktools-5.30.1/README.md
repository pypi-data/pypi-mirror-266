# pyrok-tools

Python tools used in internal Rokubun projects. This repository contains the following modules:

- `logger`, a module that extends basic Python logging
- `geodetic`, to perform basic geodetic transformation (Cartesian to Geodetic,
  Cartesian to Local Tangential Plane, ...)


## Installation

pip install roktools

## Modules

### Logger

Example of how to use the logger module:
```python
>>> from roktools import logger
>>> logger.set_level("DEBUG")
>>> logger.debug("Debug message")
2020-05-05 18:23:55,688 - DEBUG    - Debug message
>>> logger.warning("Warning message")
2020-05-05 18:24:11,327 - WARNING  - Warning message
>>> logger.info("Info message")
2020-05-05 18:24:26,021 - INFO     - Info message
>>> logger.error("Error message")
2020-05-05 18:24:36,090 - ERROR    - Error message
>>> logger.critical("Critical message")
2020-05-05 18:24:43,562 - CRITICAL - Critical message
>>> logger.exception("Exception message", ValueError("Exception message")
2020-05-05 18:25:11,360 - CRITICAL - Exception message
ValueError: Exception message
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/Users/alexlopez/Work/00.General/01.Software/py-roktools/roktools/logger.py", line 46, in exception
    raise exception
ValueError: Exception message
```


## Deployment to PyPi

The project is published automatically using internal Gitlab CI on each commit to master to PyPi repository [roktools](https://pypi.org/project/roktools/)

    
