import os
from utils import sh

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
    out = sh("""cada 'ls *' -q""")
    assert out == ['bar.txt', 'baz.txt', 'foo.txt']
    
def test_index():
    out = sh("""cada 'mv * {i}' -d""")
    assert out == ['mv bar.txt 1', 'mv baz.txt 2', 'mv foo.txt 3']

def test_index0():
    out = sh("""cada 'mv * {i0}' -d""")
    assert out == ['mv bar.txt 0', 'mv baz.txt 1', 'mv foo.txt 2']

def test_index_reversed():
    out = sh("""cada 'mv * {i}' -rd""")
    assert out == ['mv foo.txt 1', 'mv baz.txt 2', 'mv bar.txt 3']
    
def test_index_with_sort_key():
    out = sh("""cada 'mv * {i}' -k "s[2]" -s 'simple' -d""")
    assert out == ['mv foo.txt 1', 'mv bar.txt 2', 'mv baz.txt 3']

def test_extra_expression():
    out = sh("""cada 'mv * {}' 'i+10' -d""")
    assert out == ['mv bar.txt 11', 'mv baz.txt 12', 'mv foo.txt 13']
    
def test_filter():
    out = sh("""cada 'rm *' -f 's.startswith("ba")' -dq""")
    assert out == ['rm bar.txt', 'rm baz.txt']

def test_two_filters():
    out = sh("""cada 'rm *' -f 's.startswith("ba")' -f 'p.stem.endswith("r")' -dq""")
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
    out = sh("""cada 'mv foo* {}' 'sh(f"file {s} -b --mime-type")' -d""")
    assert out == ['mv foo.txt text/plain']

def test_quoting_disabled():
    out = sh("""cada 'mv foo* {:S}' '"$HOME"' -d""")
    assert out == ['mv foo.txt $HOME']

def test_quoting_enabled():
    out = sh("""cada 'mv foo* {}' '"new name"' -d""")
    assert out == ["mv foo.txt 'new name'"]

def test_q_qq():
    out = sh("""cada 'mv foo* {}' 's.replace(q, "").replace(qq, "")' -d""")
    assert out == ['mv foo.txt foo.txt']

def test_addons():
    os.environ['CADA_CONFIG_DIR'] = '../addons'
    out = sh("""cada 'mv *.txt {s}.{e}' 'md5(c)' -d""")
    assert out == ['mv bar.txt bar.txt.614dd0e977becb4c6f7fa99e64549b12', 'mv baz.txt baz.txt.7bf20d8965c6940c058380b43275e552', 'mv foo.txt foo.txt.0bee89b07a248e27c83fc3d5951213c1']
