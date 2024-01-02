# TODO

Plans to be considered in the future:

- support user-defined plugins loaded from predefined location (~/.cada/plugins)
- helper variables for reading size, c/a/m-time, r/w/x-attibs, user, group
- helper function for `sh = lambda x: check_output(x, shell=True).decode().splitlines()[0].strip()`
- ascending/descending sorting
- sorting by size, by creation date/time etc, e.g. `'mv {} {i}_{}' -k 't.c'`
