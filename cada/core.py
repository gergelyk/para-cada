import re
import glob
import shlex
import queue
import subprocess
import multiprocessing as mp
from itertools import product
from pathlib import Path
from importlib import import_module

import glob2
import natsort
from click import ClickException

from cada.printer import ReservedPrinter
from cada.xpath import XPath
from cada.addons import plugins, symbols, LazyLocals, load_startup_module

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

class Index(int):

    @property
    def every(self):
        return int(self)

    @property
    def qual(self):
        try:
            return self._qual
        except AttributeError:
            raise NotImplementedError("'qual' is not available in multi-processing mode")

    @qual.setter
    def qual(self, value):
        self._qual = value
    
    @property
    def total(self):
        return self._total

    @total.setter
    def total(self, value):
        self._total = value

reserved_printer = ReservedPrinter()

sort_algs = {
    'none': lambda x, r, k: reversed(x) if r else x,
    'simple': lambda x, r, k: sorted(x, reverse=r, key=k),
    'natural': lambda x, r, k: natsort.natsorted(x, reverse=r, key=k),
    'natural-ignore-case': lambda x, r, k: natsort.natsorted(x, alg=natsort.ns.IGNORECASE, reverse=r, key=k),
}

err_queue = mp.Queue(1)
progress = mp.Value('I', 0)
CMD_SEP = '###'
CMD_PREFIX = '$ '

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
    try:
        parts = symbol.split('.')
        mod_name = parts[0]
        attr_names = parts[1:]
        mod = import_module(mod_name)
        res = mod
        for a in attr_names:
            res = getattr(res, a)
    except Exception as exc:
        raise ClickException(f"Cannot import {symbol!r}: {exc}") from exc
    return (parts[-1], res)


def format_context(ctx):
    return f'context: {", ".join(map(repr, ctx))}'

def call_guarded(ctx, f, *args, **kwargs):
    try:
        return f(*args, **kwargs)
    except Exception as exc:
        ctx = format_context(ctx)
        raise UserError(f"{CMD_SEP} Error in {f.__name__}(): {exc} [{ctx}]") from exc

def skip_command(ctx):
    ctx = format_context(ctx)
    increment_progress()
    raise SkipCommand(f"{CMD_SEP} Skipped [{ctx}]")

class Runner:
    
    def __init__(self, command_expr, eval_expr, dry_run, jobs, filter_, include_hidden, import_, color, quiet, sort_alg_name, sort_key, reverse, stop_at_error):
        self._eval_expressions = eval_expr
        self._dry_run = dry_run
        self._jobs = jobs
        self.filters = filter_
        self._include_hidden = include_hidden
        self._import = import_
        self._quiet = quiet
        self._color = (color == 'auto' and reserved_printer.is_tty) or (color == 'always')
        self._stop_at_error = stop_at_error
        self._executor = self._run_in_dry_mode if self._dry_run else self._run_in_shell
        self._cmd_parts = shlex.split(command_expr)
        self._glob_detections = list(map(is_glob, self._cmd_parts))
        self._glob_indices = [i for i, d in enumerate(self._glob_detections) if d]
        globs = [p for p, d in zip(self._cmd_parts, self._glob_detections) if d]
        sort_alg = sort_algs[sort_alg_name]
        
        if sort_key is None:
            sort_key_outer = None
        else:
            if sort_alg_name != 'simple':
                raise ClickException('--sort-key is supported only with --sort-alg=simple')
            sort_key_inner = eval('lambda s, p, x: ' + sort_key)
            sort_key_outer = lambda s: sort_key_inner(s, Path(s), XPath(s))
        
        globs_expanded = [sort_alg(glob2.glob(g, include_hidden=self._include_hidden), reverse, sort_key_outer) for g in globs]
        self._globs_product = list(product(*globs_expanded))
        self._total = len(self._globs_product)
        self._skipped_number = 0
        
        load_startup_module()
        
        if not self._color:
            reserved_printer.set_monohrome()

    def _run_in_dry_mode(self, cmd):
        with reserved_printer as printer:
            printer.show_blue(CMD_PREFIX + cmd)


    def _run_in_shell(self, cmd):
        if not self._quiet and reserved_printer.is_tty:
            with reserved_printer as printer:
                printer.clear_line()
                if self._jobs is None:
                    printer.show_blue(CMD_PREFIX + cmd + '  ', end='')
                printer.show_blue(f'{CMD_SEP} [progress: {progress.value} of {self._total}]', end='')
                
        proc = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        increment_progress()

        with reserved_printer as printer:
            if not self._quiet:
                printer.clear_line()
                if proc.returncode:
                    printer.show_red(f"{CMD_PREFIX}{cmd}  {CMD_SEP} [returned: {proc.returncode}]")
                else:
                    printer.show_green(CMD_PREFIX + cmd)

            printer.show(proc.stdout.decode(), end='')
        
        if proc.returncode:
            raise CommandFailure(f'Command returned {proc.returncode}')

    def _run_single(self, args):
        index_int, product_item = args
        index0 = Index(index_int)
        index = Index(index_int + 1)
        index.total = index0.total = self._total
        if self._jobs is None:
            index0.qual = index0 - self._skipped_number
            index.qual = index - self._skipped_number
            
        context_vars = {'i': index, 'i0': index0}
        product_dict = dict(zip(self._glob_indices, product_item))
        
        plugins_instance = plugins.get_instance(tuple(product_dict.values()))
        lazy_plugins_instance = LazyLocals(plugins_instance)
        context_strings = {'s' + str(i): v for i, v in enumerate(product_dict.values())}
        context_paths = {'p' + str(i): Path(v) for i, v in enumerate(product_dict.values())}
        context_stats = {'x' + str(i): XPath(v) for i, v in enumerate(product_dict.values())}
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
            **symbols,
            **context_vars,
            **context_strings,
            **context_paths,
            **context_stats,
            **context_common,
            **context_imports
        )

        for f in self.filters:
            if not call_guarded(product_item, eval, f, context_full, lazy_plugins_instance):
                skip_command(product_item)

        expr_vals = [call_guarded(product_item, eval, e, context_full, lazy_plugins_instance) for e in self._eval_expressions]

        context_exprs = {'e' + str(i): v for i, v in enumerate(expr_vals)}
        if expr_vals:
            context_exprs['e'] = context_exprs['e0']

        if expr_vals:
            default_arg = (expr_vals[0],)
        elif product_dict:
            default_arg = (next(iter(product_dict.values())),)
        else:
            default_arg = ()

        context_formatting = {**symbols, **plugins_instance, **context_vars, **context_strings, **context_paths, **context_stats, **context_exprs}
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
            self._skipped_number += 1
            if not self._quiet:
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
