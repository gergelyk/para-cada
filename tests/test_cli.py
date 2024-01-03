import re
import pytest
import subprocess
from pathlib import Path

def sh(cmd, cwd="tests/data"):
    return subprocess.check_output(f'cd {cwd} && ' + cmd + ' 2>&1 | cat', stderr=subprocess.STDOUT, shell=True).decode().splitlines()

def test_version():
    out = sh("""cada -V""")
    assert out[0].startswith('cada, version')
    
def test_help():
    out = sh("""cada -h""")
    assert out[0].startswith('Usage: cada [OPTIONS]')
    
def test_dry_run_ls():
    out = sh("""cada 'ls *' -d""")
    assert out == ['ls bar.txt', 'ls baz.txt', 'ls foo.txt']

def test_real_run_ls():
    out = sh("""cada 'ls *' -s""")
    assert out == ['bar.txt', 'baz.txt', 'foo.txt']
    
def test_index():
    out = sh("""cada 'mv * {i}' -d""")
    assert out == ['mv bar.txt 0', 'mv baz.txt 1', 'mv foo.txt 2']

def test_extra_expression():
    out = sh("""cada 'mv * {}' 'i+10' -d""")
    assert out == ['mv bar.txt 10', 'mv baz.txt 11', 'mv foo.txt 12']
    
def test_filter():
    out = sh("""cada 'rm *' -f 's.startswith("ba")' -ds""")
    assert out == ['rm bar.txt', 'rm baz.txt']

def test_two_filters():
    out = sh("""cada 'rm *' -f 's.startswith("ba")' -f 'p.stem.endswith("r")' -ds""")
    assert out == ['rm bar.txt']

def test_string_var():
    out = sh("""cada 'true foo* {} {} {s} {s0}' -d""")
    assert out == ['true foo.txt foo.txt foo.txt foo.txt foo.txt']

def test_path_var():
    out = sh("""cada 'true foo* {p.stem} {p0.stem}' -d""")
    assert out == ['true foo.txt foo foo']

def test_xpath_var():
    out = sh("""cada 'true foo* {x.is_file} {x0.is_dir}' -d""")
    assert out == ['true foo.txt True False']

def test_eval_import():
    out = sh("""cada 'true foo*' -f "bool(sys)" -i sys -d""")
    assert out == ['true foo.txt']

def test_eval_error():
    out = sh("""cada 'true foo*' -f "bool(sys)" -d""")
    assert out == ["### Error in eval(): name 'sys' is not defined [context: 'foo.txt']"]

def test_format_error():
    out = sh("""cada 'true foo* {w}' -d""")
    assert out == ["### Error in format(): 'w' [context: 'foo.txt']"]

def test_sh():
    out = sh("""cada 'mv foo* {}' 'sh("file {s} -b --mime-type")' -d""")
    assert out == ['mv foo.txt text/plain']

def test_xpath_atime_default():
    out = sh("""cada 'mv foo* {x.atime}' -d""")
    assert re.match(r'mv foo.txt \d\d\d\d-\d\d-\d\d', out[0])

def test_xpath_ctime_default_from_expression():
    out = sh("""cada 'mv foo* {}' 'x.ctime' -d""")
    assert re.match(r'mv foo.txt \d\d\d\d-\d\d-\d\d', out[0])
    
def test_xpath_mtime_custom():
    out = sh("""cada 'mv foo* {}' 'x.mtime("%H")' -d""")
    assert re.match(r'mv foo.txt \d\d', out[0])

def test_xpath_size():
    out = sh("""cada 'true foo* {x.size} {x.size.int} {x.size.bin} {x.size.nat}' -d""")
    assert out == ['true foo.txt 4 4 4_Bytes 4_Bytes']

def test_xpath_mode():
    out = sh("""cada 'true foo* {x.mode} {x.mode.int} {x.mode.oct}' -d""")
    assert out == ['true foo.txt 644 420 644']

def test_xpath_mode_full():
    out = sh("""cada 'true foo* {x.mode_full} {x.mode_full.int} {x.mode_full.oct}' -d""")
    assert out == ['true foo.txt 100644 33188 100644']

def test_xpath_owner():
    out = sh("""cada 'mv foo* {}' 'x.owner' -d""")
    assert re.match(r'mv foo.txt [a-z0-9]+', out[0])
    
def test_xpath_group():
    out = sh("""cada 'mv foo* {}' 'x.group' -d""")
    assert re.match(r'mv foo.txt [a-z0-9]+', out[0])

def test_xpath_is_dir():
    out = sh("""cada 'true foo* {x.is_dir}' -d""")
    assert out == ['true foo.txt False']

def test_xpath_is_file():
    out = sh("""cada 'true foo* {x.is_file}' -d""")
    assert out == ['true foo.txt True']

def test_xpath_is_symlink():
    out = sh("""cada 'true foo* {x.is_symlink}' -d""")
    assert out == ['true foo.txt False']

def test_xpath_readlink():
    out = sh("""cada 'true foo* {x.link}' -d""")
    assert out == ["### Error in format(): [Errno 22] Invalid argument: 'foo.txt' [context: 'foo.txt']"]
    
def test_xpath_name():
    out = sh("""cada 'true foo* {x.name}' -d""")
    assert out == ['true foo.txt foo.txt']
    
def test_xpath_parent():
    out = sh("""cada 'true foo* {x.parent}' -d""")
    assert out == ['true foo.txt .']
    
def test_xpath_stem():
    out = sh("""cada 'true foo* {x.stem}' -d""")
    assert out == ['true foo.txt foo']

def test_xpath_suffix():
    out = sh("""cada 'true foo* {x.suffix}' -d""")
    assert out == ['true foo.txt .txt']
    
def test_xpath_suffixes():
    out = sh("""cada 'true foo* {x.suffixes}' -d""")
    assert out == ['true foo.txt .txt']

def test_xpath_absolute():
    out = sh("""cada 'true foo* {x.absolute}' -d""")
    assert out == ['true foo.txt ' + str(Path('tests/data/foo.txt').absolute())]

