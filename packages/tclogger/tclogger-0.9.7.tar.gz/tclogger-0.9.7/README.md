# tclogger
Python terminal colored logger

![](https://img.shields.io/pypi/v/tclogger?label=tclogger&color=blue&cacheSeconds=60)

## Install
```sh
pip install tclogger
```

## Usage
```py
from tclogger import logger, int_bits, Runtimer
with Runtimer():
    logger.note("hello world")
    logger.mesg(int_bits(1234567890))

shell_cmd("ls -l")
```