from cada import plugins, symbols
from pathlib import Path
import hashlib

@plugins.register('c')
def content(s):
    return Path(s).read_bytes()

symbols['md5'] = lambda data: hashlib.md5(data).hexdigest()
