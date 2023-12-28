import click
from cada.core import run

@click.command(context_settings=dict(show_default=True, help_option_names=["-h", "--help"]))
@click.argument('command')
@click.argument('expression', nargs=-1)
@click.option('-d', '--dry-run', is_flag=True, help='Only show what would be executed.')
@click.option('-H', '--include-hidden', is_flag=True, help='Glob expression includes files that starts with period.')
@click.option('-i', '--import', 'import_', multiple=True, help='Import extra symbol used in user-defined expressions.')
@click.option('-s', '--silent', is_flag=True, help='Do not print anything except stdout/stderr of the executed commands.')
@click.option('-S', '--sort', 'sort_alg_name', type=click.Choice(['none', 'simple', 'natural', 'natural-ignore-case']), default='natural-ignore-case', help='Determines execution order.')
@click.option('-x', '--stop-at-error', is_flag=True, help='Terminates when the first command returns exit code other than 0.')
@click.version_option(None, '-V', '--version', package_name='para-cada')
def main(command, expression, **kwargs):
    """Executes your command for each file selected using glob expression(s)."""
    run(command, expression, **kwargs)

if __name__ == '__main__':
    main()
