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
| s0, s1, ..., s(*N*-1) | str      | EFC          | Title        |
| p0, p1, ..., p(*N*-1) | Path     | EFC          | Text         |
| x0, x1, ..., x(*N*-1) | XPath    | EFC          | Text         |
| e0, e1, ..., e(*M*-1) | XPath    | EFC          | Text         |
| i                     | Index    | EFC          |  |
| i0                    | Index    | EFC          |  |
| sh                    | function | EF           |  |
| re                    | module   | EF           | [Lib/re](https://docs.python.org/3/library/re.html)
| Path                  | type     | EF           | [Lib/pathlib.Path](https://docs.python.org/3/library/pathlib.html#pathlib.Path)


*N* - Number of references.
*M* - Number of *extra expressions*.

<sup>[1]</sup> Availability:
- C - Available in *command expression*.
- E - Available in *extra expressions*.
- F - Available in *format expressions*.
- K - Available in *key expression*.

<sup>[2]</sup>in *key expression* correspond to each glob


```py
lambda cmd: subprocess.check_output(cmd.format(**context_full), shell=True).decode().splitlines()[0].strip()   
```

```py
subprocess.check_output(cmd, shell=True).decode().splitlines()[0].strip()   
```

# Types

## Index

| Attribute         | Description  |
| :----             | :---         |
| every             | Alias for x0 |
| qual              | Alias for x0 |
| total             | Alias for x0 |


## XPath

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

| Attribute         | Description  |
| :----             | :---         |
| \_\_str\_\_       | Alias for x0 |
| \_\_call\_\_      | Alias for x0 |


## StSize

| Attribute         | Description  |
| :----             | :---         |
| \_\_str\_\_       | Alias for x0 |
| int               | Alias for x0 |
| nat               | Alias for x0 |
| bin               | Alias for x0 |


## StMode

| Attribute         | Description  |
| :----             | :---         |
| \_\_str\_\_       | Alias for x0 |
| int               | Alias for x0 |
| oct               | Alias for x0 |
