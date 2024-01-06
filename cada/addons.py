import os
import sys
from pathlib import Path
from importlib import import_module

STARTUP_FILENAME = 'startup.py'

def load_startup_module():
    from cada.__main__ import PROG_NAME
    config_dir_default = Path().home() / ('.' + PROG_NAME)
    config_dir = Path(os.getenv('CADA_CONFIG_DIR', config_dir_default))
    startup_path = config_dir / STARTUP_FILENAME
    if startup_path.exists():
        sys.path.insert(0, str(config_dir))
        import_module(startup_path.stem)

class PluginsRegistry:

    def __init__(self):
        self._plugins = {}

    def register(self, name):
        def register_(f):
            self._plugins[name] = f
        return register_

    def get_instance(self, product):
        inst = {}
        if product:
            inst.update( {k: LazyWrapper(v, product[0]) for k, v in self._plugins.items()} )
            inst.update( {k + str(0): v for k, v in inst.items()} )
            inst.update( {k + str(i): LazyWrapper(v, p) for k, v in self._plugins.items() for i, p in enumerate(product) if i >= 1} )
        return inst


class LazyWrapper:
    def __init__(self, func, arg):
        self._func = func
        self._arg = arg
        
    def _get_instance(self):
        return self._func(self._arg)
        
    def __str__(self):
        return str(self._get_instance())
    
    def __getattr__(self, name):
        return getattr(self._get_instance(), name)


class LazyLocals:
    
    def __init__(self, mapping):
        self._mapping = mapping
    
    def __getitem__(self, name):
        return self._mapping[name]._get_instance()

                
plugins = PluginsRegistry()
symbols = {}
