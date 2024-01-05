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

Cada knows where glob expression is. It executes entire command with subsequent values corresponding to this expression. Additionally, user may transform those values using regular Python syntax. Take a look at the examples below and the [tutorial](https://gergelyk.github.io/para-cada/).

## Installation

```sh
pip install para-cada
```
 
## Examples

It is recommended to run examples below in the *dry mode*, by adding `-d` flag. This way you will only simulate what would happen without actually applying any changes to the filesystem.

Examples below assume that there are not spaces or special characters in the filenames. Otherwise, some quotation would be required. 

```sh
# backup all the `.txt` files in the current directory
cada 'cp *.txt {}.bkp'

# restore backups above
cada 'mv *.bkp {p.stem}'

# replace `conf` and `config` by `cfg` in the file names of `.ini` files; be case insensitive
cada 'mv *.ini {}' 're.sub("conf(ig)?", "cfg", s, flags=re.IGNORECASE)'

# change file names from snake-case to camel-case, leave extensions in lower case
cada 'mv *.* {}' 'Path(s.title().replace("_", "")).with_suffix(p0.suffix.lower())'

# prepend each `.txt` file with subsequent numbers; 4 digits wide, 0-padded
cada 'mv *.txt {i:04d}_{}'

# add `.d` suffix to the names of all directories
cada 'mv * {}.d' -f x.is_dir

# print filenames where stem is shorter than 3 characters
cada 'echo *' -f 'len(p.stem) < 5' -s

# to each `.tar` file add a suffix that represents MD5 sum calculated over the file content
cada 'mv *.tar {s}.{e}' 'hashlib.md5(p.read_bytes()).hexdigest()' -i hashlib

# set executable attribute to the files with a shebang and remove it from remaining files
cada 'chmod {}x **/*' '"-+"[p.open("rb").read(2) == b"#!"]' -f x.is_file

# put your images in subdirectories according to their creation date
cada 'mkdir -p {} && mv *.jpg {}' x.ctime
    
# put your images in subdirectories according to their MIME type
cada 'mkdir -p {} && mv * {}' 'sh("file {s} -b --mime-type")'
    
# compile simple C++ project without any build system
mkdir -p build
cada 'g++ -c src/*.cpp -I inc -o build/{p.stem}.o'
g++ build/*.o -o build/app
```
