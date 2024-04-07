from sparrow.path import rel_to_abs, ls
import pickle
from typing import Union, List, Dict
import shutil
import os


def rm(*file_pattern: str, rel=False):
    """Remove files or directories.
    Example:
    --------
        >>> rm("*.jpg", "*.png")
        >>> rm("*.jpg", "*.png", rel=True)
    """
    path_list = ls(".", *file_pattern, relp=rel, concat="extend")
    for file in path_list:
        if os.path.isfile(file):
            os.remove(file)
        elif os.path.isdir(file):
            shutil.rmtree(file, ignore_errors=True)

def save(filename, data):
    import pickle
    with open(filename, "wb") as fw:
        pickle.dump(data, fw)


def load(filename):
    import pickle
    with open(filename, "rb") as fi:
        file = pickle.load(fi)
    return file


def json_load(filepath: str, rel=False, mode='rb'):
    import orjson
    abs_path = rel_to_abs(filepath, parents=1) if rel else filepath
    with open(abs_path, mode=mode) as f:
        return orjson.loads(f.read())


def json_dump(data: Union[List, Dict], filepath: str, rel=False, indent_2=False, mode='wb'):
    import orjson
    orjson_option = 0
    if indent_2:
        orjson_option = orjson.OPT_INDENT_2
    abs_path = rel_to_abs(filepath, parents=1) if rel else filepath
    with open(abs_path, mode=mode) as f:
        f.write(orjson.dumps(data, option=orjson_option))


def yaml_dump(filepath, data, rel_path=False, mode='w'):
    abs_path = rel_to_abs(filepath, parents=1) if rel_path else filepath
    from yaml import dump

    try:
        from yaml import CDumper as Dumper
    except ImportError:
        from yaml import Dumper
    with open(abs_path, mode=mode, encoding="utf-8") as fw:
        fw.write(dump(data, Dumper=Dumper, allow_unicode=True, indent=4))


def yaml_load(filepath, rel_path=False, mode='r'):
    abs_path = rel_to_abs(filepath, parents=1) if rel_path else filepath
    from yaml import load

    try:
        from yaml import CLoader as Loader
    except ImportError:
        from yaml import Loader
    with open(abs_path, mode=mode, encoding="utf-8") as stream:
        #     stream = stream.read()
        content = load(stream, Loader=Loader)
    return content
