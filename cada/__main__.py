import click
from cada.core import run

@click.command(context_settings=dict(show_default=True, help_option_names=["-h", "--help"]))
@click.argument('command')
@click.argument('expression', nargs=-1)
@click.option('-d', '--dry-run', is_flag=True, help='Number of greetings.')
@click.option('-H', '--include-hidden', is_flag=True, help='Number of greetings.')
@click.option('-i', '--import', 'import_', multiple=True, help='Number of greetings.')
@click.option('-s', '--silent', is_flag=True, help='Number of greetings.')
@click.option('-S', '--sort', 'sort_alg_name', type=click.Choice(['none', 'simple', 'natural', 'natural-ignore-case']), default='natural-ignore-case', help='Number of greetings.')
@click.option('-x', '--stop-at-error', is_flag=True, help='Number of greetings.')
@click.version_option(None, '-V', '--version', package_name='para-cada')
def main(command, expression, **kwargs):
    """Executes your command for each file selected using glob expression(s)."""
    run(command, expression, **kwargs)

if __name__ == '__main__':
    main()
