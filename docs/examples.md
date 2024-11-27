---
title: Para Cada
description: Examples
---

It is recommended to run examples below in the *dry mode*, by adding `-d` flag. This way you will only simulate what would happen without actually applying any changes to the filesystem.

```sh
# backup all the `.txt` files in the current directory
cada 'cp *.txt {}.bkp'

# restore backups above
cada 'mv *.bkp {p.stem}'

# replace `conf` and `config` by `cfg` in the file names
# of `.ini` files; be case insensitive
cada 'mv *.ini {}' 're.sub("conf(ig)?", "cfg", s, flags=re.IGNORECASE)'

# change file names from snake-case to camel-case,
# leave extensions in lower case
cada 'mv *.* {}' \
    'Path(s.title().replace("_", "")).with_suffix(p0.suffix.lower())'

# prepend each `.txt` file with subsequent numbers;
# 4 digits wide, 0-padded
cada 'mv *.txt {i:04d}_{}'

# add `.d` suffix to the names of all directories
cada 'mv * {}.d' -f x.is_dir

# print filenames where stem is shorter than 5 characters
cada 'echo *' -f 'len(p.stem) < 5' -s

# remove files from given range of time
cada 'rm *' -f '"2024-01-01" < x.ctime < "2024-01-10 12:10:00"'

# to each `.tar` file add a suffix that represents MD5 sum
# calculated over the file content
cada 'mv *.tar {s}.{e}' 'hashlib.md5(p.read_bytes()).hexdigest()' \
    -i hashlib

# set executable attribute to the files with a shebang
# and remove it from remaining files
cada 'chmod {}x **/*' '"-+"[p.open("rb").read(2) == b"#!"]' \
    -f x.is_file

# put your images in subdirectories according to their creation date
cada 'mkdir -p {} && mv *.jpg {}' x.ctime
    
# put your images in subdirectories according to their MIME type
cada 'mkdir -p {} && mv * {}' 'sh("file {s} -b --mime-type")'
    
# compile simple C++ project without any build system
mkdir -p build
cada 'g++ -c src/*.cpp -I inc -o build/{p.stem}.o'
g++ build/*.o -o build/app
```
