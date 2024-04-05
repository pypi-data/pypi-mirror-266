# tclogger
Python terminal colored logger

![](https://img.shields.io/pypi/v/tclogger?label=tclogger&color=blue&cacheSeconds=60)

## Install
```sh
pip install tclogger
```

## Usage
```py
from tclogger import logger, count_digits, Runtimer
with Runtimer():
    logger.note("hello world")
    logger.mesg(count_digits(1234567890))

shell_cmd("ls -l")
```