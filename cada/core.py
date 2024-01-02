#!/usr/bin/env python3
import sys
import glob
import shlex
import re
from itertools import product
from pathlib import Path
from importlib import import_module
from multiprocessing import Pool, Queue, Lock
from queue import Empty, Full
from itertools import repeat

import glob2
import subprocess
import natsort
from colorama import Fore, Style

err_queue = Queue(1)

class Printer:
    def __init__(self):
        self._lock = Lock()
        
    def __enter__(self):
        self._lock.acquire()
        return self
    
    def __exit__(self, *args):
        self._lock.release()
        
    def print(self, *args, **kwargs):
        print(*args, file=sys.stderr, **kwargs)

printer = Printer()

class Terminate(Exception):
    pass

class CommandFailure(RuntimeError):
    pass

class UserError(RuntimeError):
    pass 

sort_algs = {
    'none': lambda x: x,
    'simple': lambda x: sorted(x),
    'natural': lambda x: natsort.natsorted(x),
    'natural-ignore-case': lambda x: natsort.natsorted(x, alg=natsort.ns.IGNORECASE),
}

def printe(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def do_nothing(*args, **kwargs):
    pass

def run_in_dry_mode(cmd, progress, silent, show_progress):
    printe(Fore.BLUE + cmd + Style.RESET_ALL)

def run_in_shell(cmd, progress, silent, show_progress):
    echo = do_nothing if silent else printer.print
    if show_progress:
        with printer:
            echo(Fore.BLUE + f'{cmd}  ### [progress: {progress}]%' + Style.RESET_ALL, end='')
    proc = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    with printer:
        if show_progress:
            echo("\r\033[K", end='') # move caret to the begining and clear to the end of line

        if proc.returncode:
            echo(Fore.RED + f"{cmd}  ### [returned: {proc.returncode}]" + Style.RESET_ALL)
        else:
            echo(Fore.GREEN + cmd + Style.RESET_ALL)

        printer.print(proc.stdout.decode(), end='')
    
    if proc.returncode:
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


def call_guarded(ctx, f, *args, **kwargs):
    try:
        return f(*args, **kwargs)
    except Exception as exc:
        ctx = f'context: {", ".join(map(repr, ctx))}'
        raise UserError(f"### Error in {f.__name__}(): {exc} [{ctx}]") from exc

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
        
        context_strings = {'s' + str(i): v for i, v in enumerate(product_dict.values())}
        context_paths = {'p' + str(i): Path(v) for i, v in enumerate(product_dict.values())}
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
        
        expr_vals = [call_guarded(product_item, eval, e, context_full) for e in self._expressions]

        context_exprs = {'e' + str(i): v for i, v in enumerate(expr_vals)}
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
            call_guarded(product_item, p.format, *default_arg, **context_formatting)
            for i, (p, d) in enumerate(zip(self._cmd_parts, self._glob_detections))
        ]
        progress = 100 * index // len(self._globs_product)
        self._executor(' '.join(cmd_parts_expanded), progress, self._silent, self._jobs == None)

    def _run_single_guarded(self, args):
        try:
            self._run_single(args)
        except CommandFailure as exc:
            try:
                err_queue.put_nowait(3)
            except Full:
                pass
            
            if self._stop_at_error:
                raise Terminate
        except UserError as exc:
            with printer:
                printer.print(Fore.RED + str(exc) + Style.RESET_ALL)            
                sys.stderr.flush()
            try:
                err_queue.put_nowait(2)
            except Full:
                pass
            if self._stop_at_error:
                raise Terminate
        
    def run(self):       

        try:           
            if self._jobs is None or self._dry_run:
                for _ in map(self._run_single_guarded, enumerate(self._globs_product)):
                    pass
            else:
                processes = None if self._jobs == 0 else self._jobs
                with Pool(processes) as p:
                    for _ in p.imap(self._run_single_guarded, enumerate(self._globs_product)):
                        pass
        except Terminate as exc:
            pass

        try:
            # it's better to put something into the queue,
            # otherwise err_queue.get_nowait() could occassionaly raise Empty
            err_queue.put_nowait(0)
        except Full:
            pass
        
        try:
            exit_code = err_queue.get()
        except Empty:
            pass
        else:
            exit(exit_code)
