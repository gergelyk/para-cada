# para-cada

**Para cada** in Spanish means **For each**. The tool executes your command for each file selected using glob expression(s).

Why? Let's say you have multiple `.tgz` archives and you would like to extract them in one shot. In bash you can do:

```sh
ls *.tgz | xargs -IT tar xzvf T
```

or alternatively:

```sh
for T in *.tgz; do tar xzvf $T; done
```

Both options are relatively complex. This is where cada can help. Simply do:

```sh
cada 'tar xzvf *.tgz'
```

![](docs/example.png)

Cada knows where glob expression is. It executes entire command with subsequent values corresponding to this expression. Additionally, user may transform those values using regular Python syntax. Take a look at the examples below and the [tutorial](https://github.com/gergelyk/para-cada/blob/master/cada/core.py).

## Installation

```sh
pip install para-cada
```
 
## Examples

It is recommended to run examples below in the **dry mode**, by adding `-d` flag. This way you will only simulate what would happen without actually applying any changes to the filesystem.

```sh
# backup all the `.txt` files in the current directory
cada 'cp *.txt {}.bkp'

# restore backups above
cada 'mv *.bkp {}' 'p.stem'

# rename .txt files so that the names look like titles
# and extensions are in lower case
cada 'mv *.txt {}' 'Path(s0.title()).with_suffix(p0.suffix.lower())'

# replace 'config' by 'conf' in the names of the files in current dir
cada 'mv * {}' 's.replace("config", "conf")'

# prepend each text file with subsequent numbers, 0-padded
cada 'mv *.txt {i:04d}_{}'

# to each text file add a suffix that represents MD5 sum calculated over the file content
cada 'mv *.txt {s}.{e}' 'hashlib.md5(p.read_bytes()).hexdigest()' -i hashlib

# put your images in subdirectories according to their creation date
cada 'mkdir -p {e} && mv *.jpg {e}' \
    'fromtimestamp(getctime(s)).strftime("%Y-%m-%d")' \
    -i os.path.getctime -i datetime.datetime.fromtimestamp
```
