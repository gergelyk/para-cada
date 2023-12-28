# Tutorial

Let's start from creating some test data:
```sh
touch foo.txt bar.txt
```

By providing a glob expression (`*.txt`) we instruct cada to apply the command to all the expanded values one by one:

Note: Internally cada uses [glob2](https://github.com/miracle2k/python-glob2/) package, which supports recursive globbing and more.

Note: Internally cada uses `subprocess.run` with `shell=True` to run the command. This executes under `sh` by default.

```sh
cada 'ls *.txt' -d
ls bar.txt
ls foo.txt
```

When multiple glob expressions are provided, cada generates a product of them.

```sh
cada 'diff *.txt *.txt' -d
diff bar.txt bar.txt
diff bar.txt foo.txt
diff foo.txt bar.txt
diff foo.txt foo.txt
```

Variables `s0`, `s1`, `s2`...  refer to the values of subsequent glob expressions. They can be used in the command.

```sh
cada 'cp *.txt {s0}.bkp' -d
```

Note: Internally cada uses `str.format` function to render the command. This simply means that `s0` should be wrapped in curly brackets.

Users can define own expressions to modify `s` values. User-defined expressions can be referred to using `e0`, `e1`, `e2`... variables.

```sh
cada 'cp *.txt {e0}' 's0.upper()' -d
cp bar.txt BAR.TXT
cp foo.txt FOO.TXT
```

Multiple user-defined expressions can be defined. Also multiple commands can be executed when concatenated with `&&` operator of sh.

```sh
cada 'cp *.txt {e0}; cp {s0} {e1}' 's0.upper()' 's0.title()' -d
cp bar.txt BAR.TXT; cp bar.txt Bar.Txt
cp foo.txt FOO.TXT; cp foo.txt Foo.Txt
```

Because `s0`, `e0` are used very often, they are aliased as `s` and `e` respectively. Also because module `re` and `pathlib.Path` are
commonly used, they are imported by default.

```sh
cada 'mv *.txt {e}' 'Path(s).with_suffix(".md")' -d
mv bar.txt bar.md
mv foo.txt foo.md
```

Additionally, `{}` refers to the first user-defined expression. If none of them exist, `{}` to the first glob expression. Also `p0`, `p1`, `p2`... replace `Path(s0)`, `Path(s1)`, `Path(s2)`... respectively. `p` is just an alias for `p0`. This way, previous example can be simplified as:

```sh
cada 'mv *.txt {}' 'p.with_suffix(".md")' -d
mv bar.txt bar.md
mv foo.txt foo.md
```

Special value of `i` denotes index of the command.

```sh
cada 'mv *.txt {i}.txt' -d
mv bar.txt 0.txt
mv foo.txt 1.txt
```

Check `--sort` option to determine the execution order. Use user-defined expression to reverse or modify indexing.

```sh
cada 'mv *.txt {}.txt' '2-i' -d
mv bar.txt 2.txt
mv foo.txt 1.txt
```

Additional symbols can be imported using `-i` option.

```sh
cada 'mv *.txt {e0}_by_{e1}.txt' 'p.stem' 'pwd.getpwuid(os.stat(s).st_uid).pw_name' -i os -i pwd -d
mv bar.txt bar_by_gkrason.txt
mv foo.txt foo_by_gkrason.txt
```

This also allows for writing user-defined functions:

```sh
echo 'import os, pwd; owner = lambda path: pwd.getpwuid(os.stat(path).st_uid).pw_name' > owner_plugin.py
cada 'mv *.txt {e0}_by_{e1}.txt' 'p.stem' 'owner(s)' -i owner_plugin.owner -d
```

Note: Such plugins must be available in CWD or under `$PYTHONPATH`.
