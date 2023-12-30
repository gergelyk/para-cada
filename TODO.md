# TODO

Plans to be considered in the future:

- execute in multiple threads
- support user-defined plugins loaded from predefined location (~/.cada/plugins)
- helper variables for reading size, c/a/m-time, r/w/x-attibs, user, group
- ascending/descending sorting
- sorting by size, by creation date/time etc, e.g. `'mv {} {i}_{}' -k 't.c'`
- add -f EXPRESSION option to allow for filtering, e.g. cada `'rm -fr {s}' -f 'p.is_dir()'`
