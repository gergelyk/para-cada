import click
from cada.core import Runner

PROG_NAME = 'cada'

@click.command(name=PROG_NAME, context_settings=dict(show_default=True, help_option_names=["-h", "--help"]))
@click.argument('command')
@click.argument('expression', nargs=-1)
@click.option('-d', '--dry-run', is_flag=True, help='Only show what would be executed.')
@click.option('-j', '--jobs', type=int, help='Number of concurent jobs that will execute commands. 0 means `auto`.')
@click.option('-f', '--filter', 'filter_', multiple=True, help='Filter expression.')
@click.option('-H', '--include-hidden', is_flag=True, help='Glob expression includes files that starts with period.')
@click.option('-i', '--import', 'import_', multiple=True, help='Import extra symbol used in user-defined expressions.')
@click.option('-q', '--quiet', is_flag=True, help='Do not print anything except stdout/stderr of the executed commands.')
@click.option('-s', '--sort-alg', 'sort_alg_name', type=click.Choice(['none', 'simple', 'natural', 'natural-ignore-case']), default='natural-ignore-case', help='Determines execution order.')
@click.option('-r', '--reverse', is_flag=True, help='Reverse processing order.')
@click.option('-x', '--stop-at-error', is_flag=True, help='Terminates at the first command that returns code other than 0.')
@click.option('--color', type=click.Choice(['always', 'auto', 'never']), default='auto', help='When to use terminal colours.')
@click.version_option(None, '-V', '--version', package_name='para-cada', prog_name=PROG_NAME)
def main(command, expression, **kwargs):
    """Executes your command for each file selected using glob expression(s)."""
    Runner(command, expression, **kwargs).run()

if __name__ == '__main__':
    main()
