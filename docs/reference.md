---
title: Para Cada
description: Reference
---

# Symbols

| Symbol                | Type     | Availability<sup>[1]</sup> | Description |
| :----                 | :---:    | :---         | :--- |
| s                     | str      | EFCK         | Alias for s0<sup>[2]</sup> |
| p                     | Path     | EFCK         | Alias for p0<sup>[2]</sup> |
| x                     | XPath    | EFCK         | Alias for x0<sup>[2]</sup> |
| s0, s1, ..., s(*N*-1) | str      | EFC          | Resolved *Glob Expressions* |
| p0, p1, ..., p(*N*-1) | Path     | EFC          | Resolved *Glob Expressions* |
| x0, x1, ..., x(*N*-1) | XPath    | EFC          | Resolved *Glob Expressions* |
| e0, e1, ..., e(*M*-1) | XPath    | EFC          | Resolved *Eval Expressions* |
| i                     | Index    | EFC          | Ordinal number of the command, counts from 1 |
| i0                    | Index    | EFC          | Ordinal number of the command, counts from 0 |
| q                     | str      | EFC          | "'" |
| qq                    | str      | EFC          | '"' |
| *user-defined*        | *custom* | EFC          | Defined by plugins |
| sh                    | function | EF           | Executes command in shell, captures stdout [3] |
| re                    | module   | EF           | [Lib/re](https://docs.python.org/3/library/re.html) |
| Path                  | type     | EF           | [Lib/pathlib.Path](https://docs.python.org/3/library/pathlib.html#pathlib.Path) |

*N* - Number of references.
*M* - Number of *Eval Expressions*.

<sup>[1]</sup> Availability:
- C - Available in *command expression*.
- E - Available in *extra expressions*.
- F - Available in *format expressions*.
- K - Available in *key expression*.

<sup>[2]</sup> In *Key Expression* correspond to the generic *Glob Expression*.

<sup>[3]</sup> Defined as:

```py
subprocess.check_output(cmd, shell=True).decode().splitlines()[0].strip()   
```

# Types

## XPath

Wraps `pathlib.Path` denoted below as `p`.

| Attribute  | Description  |
| :----      | :---         |
|\_\_str\_\_ | str(p) |
|absolute    | p.absolute() |
|atime       | StTime(p.stat().st_atime) |
|ctime       | StTime(p.stat().st_ctime) |
|mtime       | StTime(p.stat().st_mtime) |
|mode        | StMode(p.stat().st_mode & 0o777) |
|mode_full   | StMode(p.stat().st_mode) |
|group       | p.group() |
|is_dir      | p.is_dir() |
|is_file     | p.is_file() |
|is_symlink  | p.is_symlink() |
|link        | p.readlink() |
|name        | p.name |
|owner       | p.owner() |
|parent      | p.parent |
|size        | StSize(p.stat().st_size) |
|stem        | p.stem |
|suffix      | p.suffix |
|suffixes    | ''.join(p.suffixes) |


## StTime

Represents date and time. Object `d` of `StTime` class can be used as follows:

```py
# Default string representation ('%Y-%m-%d')
str(d)

# Custom string representation
d("%Y-%m-%d %H:%M:%S")

# Comparing to other data and time
d <= '2024-01-01'
d >= '2024-01-01 12:10:00'
```

## StMode(int)

Represents mode of a file. Object `m` of `StMode` class can be used as follows:

```py
# Integer representation, int
m.int

# Octal representation, str
m.oct

# Octal representation, str (same as above)
str(m)
```

## StSize(int)

Represents size of a file. Object `s` of `StSize` class can be used as follows:

```py
# Pure int
s.int

# Human "natural" representation, str
s.nat

# Human "binary" representation, str
s.bin
```

## Index(int)

Represents ordinal number of the command. Object `i` of `Index` class can be used as follows:

```py
# Counts every command (includes skipped)
i.every

#Counts qualified commands (excludes skipped)
i.qual

#Constant value; total number of commands
i.total
```

