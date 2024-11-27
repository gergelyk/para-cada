# para-cada
![PyPI - Version](https://img.shields.io/pypi/v/para-cada)
![PyPI - License](https://img.shields.io/pypi/l/para-cada)
![PyPI - Downloads](https://img.shields.io/pypi/dm/para-cada)

[ ![](https://img.shields.io/badge/Tutorial-blue?style=for-the-badge&logo=gitbook&logoColor=white) ](https://gergelyk.github.io/para-cada/tutorial.html)
[ ![](https://img.shields.io/badge/Examples-blue?style=for-the-badge&logo=gitbook&logoColor=white) ](https://gergelyk.github.io/para-cada/examples.html)
[ ![](https://img.shields.io/badge/Reference-blue?style=for-the-badge&logo=gitbook&logoColor=white) ](https://gergelyk.github.io/para-cada/reference.html)

*Para Cada* in Spanish means *For Each*. The tool executes your command for each file selected using glob expression(s).

Why? Let's say you have multiple `.tgz` archives and you would like to extract them in one shot. Some of the options available in bash are:

```sh
ls *.tgz | xargs -IT tar xzvf T
for T in *.tgz; do tar xzvf $T; done
find . -type f -name '*.tgz' -exec tar xzvf {} \;
```

All of them are relatively complex. This is where cada can help. Simply do:

```sh
cada 'tar xzvf *.tgz'
```

<div align="center">
<img src="docs/assets/images/example.png"/>
</div>

<br>

Cada knows how glob expressions work and executes the entire command with subsequent values corresponding to your glob expression. Additionally, users may transform/filter/sort those values using regular Python syntax. Take a look at the [documentation](https://gergelyk.github.io/para-cada/).

## Installation

Requirement: Python >= 3.8

```sh
pip install para-cada
```

