# TODO

Plans to be considered in the future:

- use shlex.quote to escape args passed to the commad - this will support files with spaces in the names etc
- execute in multiple threads
- support user-defined plugins loaded from predefined location (~/.cada/plugins)
- ascending/descending sorting
- sorting by size, by creation date/time etc
- helper variables for reading size, c/a/m-time, r/w/x-attibs, user, group
- {p} and more available directly in the command; this would provide e.g. {p.stem}
- support custom formatting specifiers, e.g. {!l} for lower case, this would allow for casting boolean values to `false`/`true` used in bash and for filtering items easily, e.g. cada `'{!l} && rm -fr {s}' 'p.is_dir()'`
