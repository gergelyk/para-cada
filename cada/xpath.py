import humanize
from datetime import datetime as dt
from pathlib import Path
from functools import total_ordering


@total_ordering
class StTime:
    def __init__(self, ts_str):
        self._ts = dt.fromtimestamp(ts_str)
        
    def __str__(self):
        return self._ts.strftime("%Y-%m-%d")
    
    def __call__(self, fmt):
        return self._ts.strftime(fmt)

    def __eq__(self, other):
        return self._ts == other._ts

    def __lt__(self, other):
        return self._ts < other._ts


@total_ordering
class StSize:
    
    def __init__(self, raw):
        self._raw = raw
        
    def __str__(self):
        return str(self._raw)
    
    @property
    def int(self):
        return str(self._raw)
    
    @property
    def nat(self):
        return humanize.naturalsize(self._raw).replace(' ', '_')
        
    @property
    def bin(self):
        return humanize.naturalsize(self._raw, binary=True).replace(' ', '_')

    def __eq__(self, other):
        return self._raw == other._raw

    def __lt__(self, other):
        return self._raw < other._raw


class StMode:
    
    def __init__(self, raw):
        self._raw = raw
        
    def __str__(self):
        return self.oct
    
    @property
    def int(self):
        return str(self._raw)

    @property
    def oct(self):
        return str("{:03o}".format(self._raw))


class XPath:
    def __init__(self, path):
        self._path = Path(path)

    def __str__(self):
        return str(self._path)

    @property
    def _raw(self):
        return self._path.stat()

    @property
    def atime(self):
        return StTime(self._raw.st_atime)

    @property
    def ctime(self):
        return StTime(self._raw.st_ctime)
    
    @property
    def mtime(self):
        return StTime(self._raw.st_mtime)
    
    @property
    def size(self):
        return StSize(self._raw.st_size)

    @property
    def mode(self):
        return StMode(0o777 & self._raw.st_mode)

    @property
    def mode_full(self):
        return StMode(self._raw.st_mode)

    @property
    def owner(self):
        return self._path.owner()
    
    @property
    def group(self):
        return self._path.group()
    
    @property
    def is_dir(self):
        return self._path.is_dir()
    
    @property
    def is_file(self):
        return self._path.is_file()
    
    @property
    def is_symlink(self):
        return self._path.is_symlink()
    
    @property
    def link(self):
        return XPath(self._path.readlink())
    
    @property
    def name(self):
        return self._path.name
    
    @property
    def parent(self):
        return XPath(self._path.parent)
    
    @property
    def stem(self):
        return self._path.stem
    
    @property
    def suffix(self):
        return self._path.suffix
    
    @property
    def suffixes(self):
        return ''.join(self._path.suffixes)
    
    @property
    def absolute(self):
        return XPath(self._path.absolute())
