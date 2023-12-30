#!/usr/bin/env python3
import sys
import glob
import shlex
import re
import sys
from itertools import product
from pathlib import Path
from importlib import import_module

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

def run_in_shell(cmd, progress, silent, stop_at_error):
    echo = do_nothing if silent else print
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

def run(command, expressions, dry_run, include_hidden, import_, silent, sort_alg_name, stop_at_error):

    sort_alg = sort_algs[sort_alg_name]
    executor = run_in_dry_mode if dry_run else run_in_shell
    context_common = {'re': re, 'Path': Path}
    context_imports = dict(import_symbol(s) for s in import_)
    
    cmd_parts = shlex.split(command)
    glob_detections = list(map(is_glob, cmd_parts))
    glob_indices = [i for i, d in enumerate(glob_detections) if d]
    globs = [p for p, d in zip(cmd_parts, glob_detections) if d]
    globs_expanded = [sort_alg(glob2.glob(g, include_hidden=include_hidden)) for g in globs]
    globs_product = list(product(*globs_expanded))

    try:
        for index, product_item in enumerate(globs_product):
            context_vars = {'i': index}
            product_dict = dict(zip(glob_indices, product_item))
            
            context_strings = {'s{}'.format(i): v for i, v in enumerate(product_dict.values())}
            context_paths = {'p{}'.format(i): Path(v) for i, v in enumerate(product_dict.values())}
            if product_dict:
                context_strings['s'] = context_strings['s0']
                context_paths['p'] = context_paths['p0']

            context_full = {
                **context_vars,
                **context_strings,
                **context_paths,
                **context_common,
                **context_imports
            }
            
            expr_vals = [eval(e, context_full) for e in expressions]

            context_exprs = {'e{}'.format(i): v for i, v in enumerate(expr_vals)}
            if expr_vals:
                context_exprs['e'] = context_exprs['e0']

            if expr_vals:
                default_arg = (expr_vals[0],)
            elif product_dict:
                default_arg = (next(iter(product_dict.values())),)
            else:
                default_arg = ()

            context_formatting = {**context_vars, **context_strings, **context_exprs}
            cmd_parts_expanded = [
                product_dict[i] if d else 
                p.format(*default_arg, **context_formatting)
                for i, (p, d) in enumerate(zip(cmd_parts, glob_detections))
            ]
            progress = 100 * index // len(globs_product)
            executor(shlex.join(cmd_parts_expanded), progress, silent, stop_at_error)
    except CommandFailure:
        pass
