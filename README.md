# para-cada

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

![](docs/example.png)

Cada knows where glob expression is. It executes entire command with subsequent values corresponding to this expression. Additionally, user may transform those values using regular Python syntax. Take a look at the examples below and the [tutorial](https://github.com/gergelyk/para-cada/blob/master/docs/tutorial.md).

## Installation

```sh
pip install para-cada
```
 
## Examples

It is recommended to run examples below in the *dry mode*, by adding `-d` flag. This way you will only simulate what would happen without actually applying any changes to the filesystem.

```sh
# backup all the `.txt` files in the current directory
cada 'cp *.txt {}.bkp'

# restore backups above
cada 'mv *.bkp {}' 'p.stem'

# replace `conf` and `config` by `cfg` in the file names of `.ini` files; be case insensitive
cada 'mv *.ini {}' 're.sub("conf(ig)?", "cfg", s, flags=re.IGNORECASE)'

# change file names from snake-case to camel-case, leave extensions in lower case
cada 'mv *.* {}' 'Path(s.title().replace("_", "")).with_suffix(p0.suffix.lower())'

# prepend each `.txt` file with subsequent numbers; 4 digits wide, 0-padded
cada 'mv *.txt {i:04d}_{}'

# to each `.tar` file add a suffix that represents MD5 sum calculated over the file content
cada 'mv *.tar {s}.{e}' 'hashlib.md5(p.read_bytes()).hexdigest()' -i hashlib

# print filenames where stem is shorter than 3 characters
cada '{} && echo *' 'str(len(p.stem) < 3).lower()' -s

# set executable attribute to the files with a shebang and remove it from remaining files
cada 'chmod {e}x **/*.*' '"-+"[p.open("rb").read(2) == b"#!"]' -i subprocess.check_output

# put your images in subdirectories according to their creation date
cada 'mkdir -p {e} && mv *.jpg {e}' \
    'fromtimestamp(getctime(s)).strftime("%Y-%m-%d")' \
    -i os.path.getctime -i datetime.datetime.fromtimestamp

# put your images in subdirectories according to their MIME type
cada 'mkdir -p {e} && mv * {e}' \
    'check_output(f"file {s} -b --mime-type", shell=True).decode().strip()' \
    -i subprocess.check_output
    
# compile simple C++ project without any build system
mkdir -p build
cada 'g++ -c src/*.cpp -I inc -o build/{}.o' 'p.stem'
g++ build/*.o -o build/app
```
