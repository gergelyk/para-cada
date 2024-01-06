import re
from pathlib import Path
from utils import sh

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

