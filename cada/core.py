#!/usr/bin/env python3
import sys
import glob
import shlex
import re
import sys
from itertools import product
from pathlib import Path
from importlib import import_module
from multiprocessing import Pool, Queue
from itertools import repeat

import glob2
import subprocess
import natsort
from colorama import Fore, Style

class CommandFailure(Exception):
    pass 

sort_algs = {
    'none': lambda x: x,
    'simple': lambda x: sorted(x),
    'natural': lambda x: natsort.natsorted(x),
    'natural-ignore-case': lambda x: natsort.natsorted(x, alg=natsort.ns.IGNORECASE),
}

def do_nothing(*args, **kwargs):
    pass

def run_in_dry_mode(cmd, progress, silent, stop_at_error):
    print(Fore.BLUE + cmd + Style.RESET_ALL)

def run_in_shell(cmd, progress, silent, stop_at_error, show_progress):
    echo = do_nothing if silent else print
    if show_progress:
        echo(Fore.BLUE + f'{cmd}  ### [progress: {progress}]%' + Style.RESET_ALL, end='')
        sys.stdout.flush()
    proc = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    echo("\r\033[K", end='') # move caret to the begining and clear to the end of line

    if proc.returncode:
        echo(Fore.RED + f"{cmd}  ### [returned: {proc.returncode}]" + Style.RESET_ALL)
    else:
        echo(Fore.GREEN + cmd + Style.RESET_ALL)

    print(proc.stdout.decode(), end='')
    sys.stdout.flush()
    
    if stop_at_error and proc.returncode:
        raise CommandFailure(f'Command returned {proc.returncode}')

def is_glob(text):
    return glob.escape(text) != text

def import_symbol(symbol):
    parts = symbol.split('.')
    mod_name = parts[0]
    attr_names = parts[1:]
    mod = import_module(mod_name)
    res = mod
    for a in attr_names:
        res = getattr(res, a)
    return (parts[-1], res)


class Runner:
    
    def __init__(self, command, expressions, dry_run, jobs, include_hidden, import_, silent, sort_alg_name, stop_at_error):
        self._expressions = expressions
        self._dry_run = dry_run
        self._jobs = jobs
        self._include_hidden = include_hidden
        self._import = import_
        self._silent = silent
        self._stop_at_error = stop_at_error
        self._executor = run_in_dry_mode if self._dry_run else run_in_shell
        self._cmd_parts = shlex.split(command)
        self._glob_detections = list(map(is_glob, self._cmd_parts))
        self._glob_indices = [i for i, d in enumerate(self._glob_detections) if d]
        globs = [p for p, d in zip(self._cmd_parts, self._glob_detections) if d]
        sort_alg = sort_algs[sort_alg_name]
        globs_expanded = [sort_alg(glob2.glob(g, include_hidden=self._include_hidden)) for g in globs]
        self._globs_product = list(product(*globs_expanded))

    def _run_single(self, args):
        index, product_item = args
        context_vars = {'i': index}
        product_dict = dict(zip(self._glob_indices, product_item))
        
        context_strings = {'s{}'.format(i): v for i, v in enumerate(product_dict.values())}
        context_paths = {'p{}'.format(i): Path(v) for i, v in enumerate(product_dict.values())}
        if product_dict:
            context_strings['s'] = context_strings['s0']
            context_paths['p'] = context_paths['p0']

        # vars below cannot be pickled, therefore there they cannot be moved to __init__
        context_common = {'re': re, 'Path': Path}
        context_imports = dict(import_symbol(s) for s in self._import)

        context_full = {
            **context_vars,
            **context_strings,
            **context_paths,
            **context_common,
            **context_imports
        }
        
        expr_vals = [eval(e, context_full) for e in self._expressions]

        context_exprs = {'e{}'.format(i): v for i, v in enumerate(expr_vals)}
        if expr_vals:
            context_exprs['e'] = context_exprs['e0']

        if expr_vals:
            default_arg = (expr_vals[0],)
        elif product_dict:
            default_arg = (next(iter(product_dict.values())),)
        else:
            default_arg = ()

        context_formatting = {**context_vars, **context_strings, **context_paths, **context_exprs}
        cmd_parts_expanded = [
            shlex.quote(product_dict[i]) if d else 
            p.format(*default_arg, **context_formatting)
            for i, (p, d) in enumerate(zip(self._cmd_parts, self._glob_detections))
        ]
        progress = 100 * index // len(self._globs_product)
        self._executor(' '.join(cmd_parts_expanded), progress, self._silent, self._stop_at_error, self._jobs == None)

    def run(self):       

        try:        
            if self._jobs is None:
                list(map(self._run_single, enumerate(self._globs_product)))
            else:
                jobs = None if self._jobs == 0 else self._jobs
                with Pool(jobs) as p:
                    for _ in p.imap(self._run_single, enumerate(self._globs_product)):
                        pass
        except CommandFailure:
            pass
