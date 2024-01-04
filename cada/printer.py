import sys
import multiprocessing as mp
from colorama import Fore, Style

class PrinterImpl:

    def __init__(self):
        self.stream = sys.stderr
        self.is_tty = self.stream.isatty()
        if not self.is_tty:
            self.clear_line = lambda: None

    def set_monohrome(self):
        self.show_colored = self.show_monohrome

    def show(self, *args, **kwargs):
        print(*args, file=self.stream, **kwargs)

    def show_colored(self, color, *args, **kwargs):
        self.show(*(color + str(a) + Style.RESET_ALL for a in args), **kwargs)
        
    def show_monohrome(self, color, *args, **kwargs):
        self.show(*args, **kwargs)
        
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
    
    @property
    def is_tty(self):
        return self._impl.is_tty

    def set_monohrome(self):
        self._impl.set_monohrome()

    def __enter__(self):
        self._lock.acquire()
        return self._impl
    
    def __exit__(self, *args):
        self._impl.stream.flush()
        self._lock.release()
