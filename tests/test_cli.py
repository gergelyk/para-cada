import pytest
import subprocess

def sh(cmd, cwd="tests/data/simple"):
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
    
def test_filter():
    out = sh("""cada 'rm *' -f 's.startswith("ba")' -ds""")
    assert out == ['rm bar.txt', 'rm baz.txt']

def test_two_filters():
    out = sh("""cada 'rm *' -f 's.startswith("ba")' -f 'p.stem.endswith("r")' -ds""")
    assert out == ['rm bar.txt']
