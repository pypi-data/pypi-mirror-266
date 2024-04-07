# sparrow-python
[![image](https://img.shields.io/badge/Pypi-0.1.7-green.svg)](https://pypi.org/project/sparrow-python)
[![image](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/)
[![image](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![image](https://img.shields.io/badge/author-kunyuan-orange.svg?style=flat-square&logo=appveyor)](https://github.com/beidongjiedeguang)


-------------------------

## Install

```bash
pip install sparrow-python
# Or dev version
pip install sparrow-python[dev]
# Or
pip install -e .
# Or
pip install -e .[dev]
```

## Usage

### Multiprocessing SyncManager

Open server first:

```bash
$ spr start-server
```

The defualt port `50001`.

(Process1) productor:

```python
from sparrow.multiprocess.client import Client

client = Client(port=50001)
client.update_dict({'a': 1, 'b': 2})
```

(Process2) consumer:

```python
from sparrow.multiprocess.client import Client

client = Client(port=50001)
print(client.get_dict_data())

>> > {'a': 1, 'b': 2}
```

### Common tools

- **Kill process by port**

```bash
$ spr kill {port}
```

- **pack & unpack**  
  support archive format: "zip", "tar", "gztar", "bztar", or "xztar".

```bash
$ spr pack pack_dir
```

```bash
$ spr unpack filename extract_dir
```

- **Scaffold**

```bash
$ spr create awosome-project
```

### Some useful functions

> `sparrow.relp`  
> Relative path, which is used to read or save files more easily.

> `sparrow.performance.MeasureTime`  
> For measuring time (including gpu time)

> `sparrow.performance.get_process_memory`  
> Get the memory size occupied by the process

> `sparrow.performance.get_virtual_memory`  
> Get virtual machine memory information

> `sparrow.add_env_path`  
> Add python environment variable (use relative file path)

### Safe logger in `multiprocessing`

```python
from sparrow.log import Logger
import numpy as np

logger = Logger(name='train-log', log_dir='./logs', )
logger.info("hello", "numpy:", np.arange(10))

logger2 = Logger.get_logger('train-log')
print(id(logger2) == id(logger))
>> > True
```
