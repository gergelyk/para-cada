import sys
import re
import glob
import shlex
import queue
import subprocess
import multiprocessing as mp
from itertools import product
from pathlib import Path
from importlib import import_module
from itertools import repeat
from datetime import datetime as dt

import glob2
import natsort
import humanize
from colorama import Fore, Style

class Terminate(Exception):
    pass

class SkipCommand(Exception):
    pass

class CommandFailure(RuntimeError):
    pass

class UserError(RuntimeError):
    pass 


class EXIT_CODE:
    SUCCESS = 0
    CMD_GENERATION_ERROR = 2
    CMD_EXECUTION_ERROR = 3


class StTime:
    def __init__(self, ts_str):
        self._ts = dt.fromtimestamp(ts_str)
        
    def __str__(self):
        return self._ts.strftime("%Y-%m-%d")
    
    def __call__(self, fmt):
        return self._ts.strftime(fmt)

class StSize:
    
    def __init__(self, raw):
        self._raw = raw
        
    def __str__(self):
        return self.raw
    
    @property
    def int(self):
        return str(self._raw)
    
    @property
    def nat(self):
        return humanize.naturalsize(self._raw).replace(' ', '_')
        
    @property
    def bin(self):
        return humanize.naturalsize(self._raw, binary=True).replace(' ', '_')

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
        self._path = path

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
    def mode_full(self):
        return StMode(self._raw.st_mode)
    
    @property
    def mode(self):
        return StMode(0o777 & self._raw.st_mode)
    
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

class PrinterImpl:

    def show(self, *args, **kwargs):
        print(*args, file=sys.stderr, **kwargs)

    def show_colored(self, color, *args, **kwargs):
        self.show(*(color + str(a) + Style.RESET_ALL for a in args), **kwargs)
        
    def show_blue(self, *args, **kwargs):
        self.show_colored(Fore.BLUE, *args, **kwargs)
        
    def show_green(self, *args, **kwargs):
        self.show_colored(Fore.GREEN, *args, **kwargs)
        
    def show_red(self, *args, **kwargs):
        self.show_colored(Fore.RED, *args, **kwargs)
        
    def show_yellow(self, *args, **kwargs):
        self.show_colored(Fore.YELLOW, *args, **kwargs)

    def clear_line(self):
        """move caret to the begining and clear to the end of line"""
        self.show("\r\033[K", end='')


class ReservedPrinter:
    def __init__(self):
        self._lock = mp.Lock()
        self._impl = PrinterImpl()
        
    def __enter__(self):
        self._lock.acquire()
        return self._impl
    
    def __exit__(self, *args):
        sys.stderr.flush()
        self._lock.release()


reserved_printer = ReservedPrinter()

sort_algs = {
    'none': lambda x: x,
    'simple': lambda x: sorted(x),
    'natural': lambda x: natsort.natsorted(x),
    'natural-ignore-case': lambda x: natsort.natsorted(x, alg=natsort.ns.IGNORECASE),
}

err_queue = mp.Queue(1)
progress = mp.Value('I', 0)
SEP = '###'

def is_glob(text):
    return glob.escape(text) != text

def increment_progress():
    with progress.get_lock():
        progress.value += 1

def queue_try_put(que, val):
    try:
        que.put_nowait(val)
    except queue.Full:
        pass

def import_symbol(symbol):
    parts = symbol.split('.')
    mod_name = parts[0]
    attr_names = parts[1:]
    mod = import_module(mod_name)
    res = mod
    for a in attr_names:
        res = getattr(res, a)
    return (parts[-1], res)


def format_context(ctx):
    return f'context: {", ".join(map(repr, ctx))}'

def call_guarded(ctx, f, *args, **kwargs):
    try:
        return f(*args, **kwargs)
    except Exception as exc:
        ctx = format_context(ctx)
        raise UserError(f"{SEP} Error in {f.__name__}(): {exc} [{ctx}]") from exc

def skip_command(ctx):
    ctx = format_context(ctx)
    increment_progress()
    raise SkipCommand(f"{SEP} Skipped [{ctx}]")

class Runner:
    
    def __init__(self, command, expressions, dry_run, jobs, filter_, include_hidden, import_, silent, sort_alg_name, stop_at_error):
        self._expressions = expressions
        self._dry_run = dry_run
        self._jobs = jobs
        self.filters = filter_
        self._include_hidden = include_hidden
        self._import = import_
        self._silent = silent
        self._stop_at_error = stop_at_error
        self._executor = self._run_in_dry_mode if self._dry_run else self._run_in_shell
        self._cmd_parts = shlex.split(command)
        self._glob_detections = list(map(is_glob, self._cmd_parts))
        self._glob_indices = [i for i, d in enumerate(self._glob_detections) if d]
        globs = [p for p, d in zip(self._cmd_parts, self._glob_detections) if d]
        sort_alg = sort_algs[sort_alg_name]
        globs_expanded = [sort_alg(glob2.glob(g, include_hidden=self._include_hidden)) for g in globs]
        self._globs_product = list(product(*globs_expanded))
        self._total = len(self._globs_product)

    def _run_in_dry_mode(self, cmd):
        with reserved_printer as printer:
            printer.show_blue(cmd)


    def _run_in_shell(self, cmd):
        if not self._silent:
            with reserved_printer as printer:
                printer.clear_line()
                if self._jobs == None:
                    printer.show_blue(cmd + '  ', end='')
                printer.show_blue(f'{SEP} [progress: {progress.value} of {self._total}]', end='')
                
        proc = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        increment_progress()

        with reserved_printer as printer:
            if not self._silent:
                printer.clear_line()
                if proc.returncode:
                    printer.show_red(f"{cmd}  {SEP} [returned: {proc.returncode}]")
                else:
                    printer.show_green(cmd)

            printer.show(proc.stdout.decode(), end='')
        
        if proc.returncode:
            raise CommandFailure(f'Command returned {proc.returncode}')

    def _run_single(self, args):
        index, product_item = args
        context_vars = {'i': index}
        product_dict = dict(zip(self._glob_indices, product_item))
        
        context_strings = {'s' + str(i): v for i, v in enumerate(product_dict.values())}
        context_paths = {'p' + str(i): Path(v) for i, v in enumerate(product_dict.values())}
        context_stats = {'x' + str(i): XPath(Path(v)) for i, v in enumerate(product_dict.values())}
        if product_dict:
            context_strings['s'] = context_strings['s0']
            context_paths['p'] = context_paths['p0']
            context_stats['x'] = context_stats['x0']

        context_full = {}
        
        # vars below cannot be pickled, therefore there they cannot be moved to __init__
        context_common = {
            're': re,
            'Path': Path,
            'sh': lambda cmd: subprocess.check_output(cmd.format(**context_full), shell=True).decode().splitlines()[0].strip()            
        }
        context_imports = dict(import_symbol(s) for s in self._import)

        context_full.update(
            **context_vars,
            **context_strings,
            **context_paths,
            **context_stats,
            **context_common,
            **context_imports
        )

        for f in self.filters:
            if not call_guarded(product_item, eval, f, context_full):
                skip_command(product_item)

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

        context_formatting = {**context_vars, **context_strings, **context_paths, **context_stats, **context_exprs}
        cmd_parts_expanded = [
            shlex.quote(product_dict[i]) if d else 
            call_guarded(product_item, p.format, *default_arg, **context_formatting)
            for i, (p, d) in enumerate(zip(self._cmd_parts, self._glob_detections))
        ]
        self._executor(' '.join(cmd_parts_expanded))

    def _run_single_guarded(self, args):
        try:
            self._run_single(args)
        except CommandFailure as exc:
            queue_try_put(err_queue, EXIT_CODE.CMD_EXECUTION_ERROR)            
            if self._stop_at_error:
                raise Terminate
        except SkipCommand as exc:
            if not self._silent:
                with reserved_printer as printer:
                    printer.clear_line()
                    printer.show_yellow(exc)
        except UserError as exc:
            with reserved_printer as printer:
                printer.show_red(exc)
            queue_try_put(err_queue, EXIT_CODE.CMD_GENERATION_ERROR)
            if self._stop_at_error:
                raise Terminate
        
    def run(self):       

        try:           
            if self._jobs is None or self._dry_run:
                for _ in map(self._run_single_guarded, enumerate(self._globs_product)):
                    pass
            else:
                processes = None if self._jobs == 0 else self._jobs
                with mp.Pool(processes) as p:
                    for _ in p.imap(self._run_single_guarded, enumerate(self._globs_product)):
                        pass
        except Terminate as exc:
            pass

        # it's better to put something into the queue,
        # otherwise err_queue.get_nowait() could occassionaly raise queue.Empty
        queue_try_put(err_queue, EXIT_CODE.SUCCESS)
        
        try:
            exit_code = err_queue.get()
        except queue.Empty:
            pass
        else:
            exit(exit_code)
