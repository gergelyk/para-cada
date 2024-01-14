---
title: Para Cada
description: Tutorial
---

# First Steps

Let's start this tutorial from creating some test data:

```sh
$ touch foo.txt bar.txt spam.md
```

Great! Now let's assume we would like to upload them to the website. We can use `curl`. This way however we can upload only one file at a time. For instance:

```sh
$ curl -s --upload-file foo.txt https://free.keep.sh
https://free.keep.sh/dsskGraWgwRsb1Hn/foo.txt
```

This is where cada helps. Replace your filename with a glob expression. Cada will expand it to corresponding filenames. Then it will execute your command for each filename separately:

```sh
$ cada 'curl -s --upload-file * https://free.keep.sh' -q
https://free.keep.sh/xv4vB1RrSR3OoF4l/bar.txt
https://free.keep.sh/Wxze2qCtWfAGccLC/foo.txt
https://free.keep.sh/qUpsaKkbPariiKnx/spam.md
```

You can even add `-j0` flag and cada will execute commands concurrently.

Flag `-q` in the example above makes cada *quiet*. This way, only stdout/stderr of executed command is forwarded to the terminal.

It is also wise to add `-d` flag when you aren't sure what you are doing. This enables so called *dry mode*. In this mode, cada will not execute any commands. It will only show what would be executed.

```sh
$ cada 'curl -s --upload-file * https://free.keep.sh' -d
curl -s --upload-file bar.txt https://free.keep.sh
curl -s --upload-file foo.txt https://free.keep.sh
curl -s --upload-file spam.md https://free.keep.sh
```

*Dry mode* can be also used to fine tune the commands before execution. You can do:

```sh
# create a script
$ cada 'curl -s --upload-file *.* https://free.keep.sh' -d > script

# edit your script
vim script

# execute your script
sh script  
```

Note that glob expression in the example above has been changed to `*.*`. This way `script` itself is not uploaded. Of course any other glob expressions are allowed here. Cada uses [glob2](https://pypi.org/project/glob2/) module to expand them. Check `cada --help` for more options that affect expansion.

Another useful option is `-x`. It stops processing as soon as any command fails (exits with the code other than 0).

# Expressions

Expression that we used to specify our command in the previous chapter is called *Command Expressoin*. It can be followed by one or more *Eval Expressions* used for defining values that can be inserted into *Command Expressoin*.

Additionally, cada uses *Filter Expressions* added by `-f` flag and *Key Expressions* added by `-k` flag. Former one is used for filtering values provided by *Glob Expressions*, while the latter one is used for sorting them. Both of them are applied before commands are executed.


## Command Expression

It can include multiple *Glob Expressions*. Cada expands each expression and calculates product of expanded values. Then it executes your command for each item of the product. For example:

```sh
$ cada 'diff *.txt *.txt' -d
diff bar.txt bar.txt
diff bar.txt foo.txt
diff foo.txt bar.txt
diff foo.txt foo.txt
```

Im most of the situations it is desired to repeat value of the *Glob Expression* instead of calculating a product. This is where `{pX}` can be used. *X* corresponds to the index of the *Glob Expression*. For instance:

```sh
cada 'cp *.txt {p0}.bkp' -d
cp bar.txt bar.txt.bkp
cp foo.txt foo.txt.bkp
```

Typically we have only one *Glob Expression*. This is why `p` is an alias for `p0`.

Note: Cada uses `str.format()` function from Python standard library to produce the final command. Command is executed using `subprocess.run` with `shell=True`, which defaults to `sh` shell.

Aforementioned `p` is an object of `pathlib.Path` and its attributes can be used directly in the `Command Expression`:

```sh
$ cada 'mv *.bkp {p.stem}' -d
mv bar.txt.bkp bar.txt
mv foo.txt.bkp foo.txt
```

Beside `p`, `p0`, `p1`..., there is also `s`, `s0`, `s1`..., and `x`, `x0`, `x1`...

Those `s` are `str` objects corresponding to the same filenames as `p`. They don't have significant meaning in *Command Expressions*, but we will see them later in this tutorial.

Those `x` in turn are objects of [XPath](reference.html#xpath) class. Essentially this is `Path` class where methods has been replaced by properties, so that they can be used in the *Command Expressions*. Note that this `XPath` has nothing to do with [this](https://en.wikipedia.org/wiki/XPath) one. Sample usage:

```sh
$ cada 'mv *.txt {x.stem}_by_{x.owner}{x.suffix}' -d
mv bar.txt bar_by_gergelyk.txt
mv foo.txt foo_by_gergelyk.txt
```

References mentioned above can be used in the *Command Expression* before or after corresponding *Glob Expression*. *Command Expression* can define a compound command. Let's have a look:

```sh
$ cada 'mkdir -p by_{x.stem} && mv *.txt {x.stem}_by_{x.owner}{x.suffix}' -d
mv bar.txt bar_by_gergelyk.txt
mv foo.txt foo_by_gergelyk.txt
```

Additionally, `i` is a special variable that is the ordinal number of the command. Variable `i0` is the same thing, but starts counting from 0.

```sh
$ cada 'mv *.txt {i:04d}_{}' -d
mv bar.txt 0001_bar.txt
mv foo.txt 0002_foo.txt
```

Finally `q` is a constant that value of which is a quote. Similarly `qq` is a double quote. This can sometimes help to avoid complex escaping.

## Eval Expressions

Sometimes there is a need of more advanced text processing than it is possible in *Command Expression*. This is when we use *Eval Expressions* where Python syntax applies. References `p`, `s`, `x` mentioned before are available here as variables. Value of the first *Eval Expressions* can be dereferenced in *Command Expression* using `e0`, or simply `e`. Following *Eval Expressions* correspond to `e1`, `e2` etc. Example:

```sh
$ cada 'mv *.txt {e}' 's.upper()' -d
mv bar.txt BAR.TXT
mv foo.txt FOO.TXT
```

There is one more aid in *Command Expression* defined for your convenience. This is `{}` which corresponds to `{e0}`, or to `{s0}` if there are no *Eval Expressions* defined.

Note: Before applying `str.format()` function, cada splits *Command Expression* into parts using `shlex.split()`. Function `str.format()` is applied to each part independently.

Some of the commonly used [symbols](reference.html#symbols), like `Path` are immediately available within *Eval Expressions*:

```sh
$ cada 'mv *.txt {}' 'Path(s.title()).with_suffix(x.suffix)' -d
mv bar.txt Bar.txt
mv foo.txt Foo.txt
```

Additional symbols can be imported using `-i` option:

```sh
$ cada 'mv *.txt {s}.{e}' 'md5(p.read_bytes()).hexdigest()' -d \
    -i hashlib.md5
mv bar.txt bar.txt.d41d8cd98f00b204e9800998ecf8427e
mv foo.txt foo.txt.d41d8cd98f00b204e9800998ecf8427e
```

Modules from CWD can be imported too. This way we can define multi-line code:
```py
# checksum.py
import hashlib

def md5(p):
    content = p.read_bytes()
    chksum = hashlib.md5(content)
    return chksum.hexdigest()
```

```sh
$ cada 'mv *.txt {s}.{e}' 'md5(p)' -i checksum.md5 -d
mv bar.txt bar.txt.d41d8cd98f00b204e9800998ecf8427e
mv foo.txt foo.txt.d41d8cd98f00b204e9800998ecf8427e
```

Cada also supports plugins that can you can use to define your own symbols and references. This will be covered in a separate chapter.

Note that values of *Glob Expressions* and *Eval Expressions* are quoted before they are inserted into final command. In very rare situations this may not be intended and in case of *Eval Expressions* it can be disabled by `S` specifier. For example:

```sh
cada 'cp *.txt {:S}' '"$HOME"' -d
cp bar.txt $HOME
cp foo.txt $HOME
```

## Filter Expressions

They can be used to select which of the items should processed. Python syntax applies here, so this gives more possibilities comparing to the *Glob Expressions* alone.

```sh
$ cada 'tar czvf {x.stem}.tgz *' -f 'len(p.stem) <= 6' -d
tar czvf bar.tgz bar.txt
### Skipped [context: 'bar.txt.bkp']
tar czvf foo.tgz foo.txt
### Skipped [context: 'foo.txt.bkp']
tar czvf script.tgz script
tar czvf spam.tgz spam.md
```

Multiple filters are allowed. All of them must be fulfilled to have the item qualified for processing:

```sh
# let's create a script with shebang
(echo '#!/bin/sh'; cat script) > script2

# add executable attribute to each file with a shebang
cada 'chmod +x *' -f 'x.is_file' -f 'p.open("rb").read(2) == b"#!"' -d
### Skipped [context: 'bar.txt']
### Skipped [context: 'bar.txt.bkp']
### Skipped [context: 'foo.txt']
### Skipped [context: 'foo.txt.bkp']
### Skipped [context: 'script']
chmod +x script2
### Skipped [context: 'spam.md']
```

Variables `i` and `i0` have special attributes to specify which of the files should be counted. For instance `i.qual` doesn't increment at the items that are skipped. Note that this attribute is not available in concurrent processing mode (with `-j` option). Check [documentation](reference.html#index) for more details.

```sh
$ cada 'mv * file_{i.qual}' -f 'x.suffix != ".bkp"' -dq
mv bar.txt file_1
mv foo.txt file_2
mv script file_3
mv script2 file_4
mv spam.md file_5
```

## Key Expressions and Sorting

Sorting determines the order of command execution. There are three things to consider:

Sorting algorithm - set by `-s` option. By default cada uses [natsort](https://pypi.org/project/natsort/) library that provides human-friendly, case-insensitive order. Other options are: 
- `natural` - Same as default, but case-sensitive.
- `simple` - Implemented by Python-native `sort()` function. We need this for user-defined sorting key.
- `none` - When execution order is not important. This may give some performance improvement on a big set of items.

Sorting direction - switched by `-r` option. Simply determines if we ascend or descend on the list of items.

Key used for sorting - determined by `-k` option. It is provided as a *Key Expression*, which is yet another expression where Python syntax and variables mentioned above apply.

The same sorting strategy is applied to the items of each *Glob Expression*. Sorting is especially useful when we rename files in bulk. Let's have a look at some examples:

```sh
# number files by creation time, starting form the oldest one
$ cada 'mv *.txt* {i}_{}' -k 'x.ctime' -s simple -d
mv bar.txt 1_bar.txt
mv foo.txt 2_foo.txt
mv bar.txt.bkp 3_bar.txt.bkp
mv foo.txt.bkp 4_foo.txt.bkp
```

```sh
# number files by size, starting form the largest one
$ cada 'mv s* {i}_{}' -k 'x.size' -s simple -r -d
mv script2 1_script2
mv script 2_script
mv spam.md 3_spam.md
```

## Plugins

Each time at startup, cada loads `~/.cada/startup.py` file (as long as it exists and is readable). This is a good place where we can define extra symbols and plugins.

Symbols can be simply added to `cada.symbols` dictionary. They are later available in the expressions (except for the *Key Expression*). For instance:

```py
from cada import symbols
import hashlib

symbols['md5'] = lambda data: hashlib.md5(data).hexdigest()
```

Now one of the previous examples can be refactored to:

```sh
$ cada 'mv *.txt {s}.{e}' 'md5(p.read_bytes())' -d
mv bar.txt bar.txt.d41d8cd98f00b204e9800998ecf8427e
mv foo.txt foo.txt.d41d8cd98f00b204e9800998ecf8427e
```

By defining a plugin we provide a definition of our new reference. Let's add reference `c` to our `startup.py`:

```py
from cada import plugins, symbols
from pathlib import Path
import hashlib

@plugins.register('c')
def content(s):
    return Path(s).read_bytes()

symbols['md5'] = lambda data: hashlib.md5(data).hexdigest()
```

Since now, `c0`, `c1` etc are available. They correspond to the subsequent *Glob Expressions* and represent content of the files. Also `c` is created as an alias for `c0`. Note that references are obtained lazily - only when they are needed.

Now we can simplify our example even further:

```sh
$ cada 'mv *.txt {s}.{e}' 'md5(c)' -d
mv bar.txt bar.txt.d41d8cd98f00b204e9800998ecf8427e
mv foo.txt foo.txt.d41d8cd98f00b204e9800998ecf8427e
```

