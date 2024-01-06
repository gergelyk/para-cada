import click
from click_help_colors import HelpColorsGroup, HelpColorsCommand
from cada.core import Runner

PROG_NAME = 'cada'

@click.command(cls=HelpColorsCommand, help_headers_color='yellow', help_options_color='blue', name=PROG_NAME, context_settings=dict(show_default=True, help_option_names=["-h", "--help"]))
@click.argument('COMMAND_EXPR')
@click.argument('EVAL_EXPR', nargs=-1)
@click.option('-H', '--include-hidden', is_flag=True, help='Include files that starts with period.')
@click.option('-f', '--filter', 'filter_', multiple=True, help='Determines which files to skip.')
@click.option('-s', '--sort-alg', 'sort_alg_name', type=click.Choice(['none', 'simple', 'natural', 'natural-ignore-case']), default='natural-ignore-case', help='Determines execution order.')
@click.option('-k', '--sort-key', help='Key expression used for sorting.')
@click.option('-r', '--reverse', is_flag=True, help='Reverse execution order.')
@click.option('-i', '--import', 'import_', multiple=True, help='Import extra symbol used in eval-expressions.')
@click.option('-d', '--dry-run', is_flag=True, help='Do not execute commands. Only show what would be executed.')
@click.option('-x', '--stop-at-error', is_flag=True, help='Terminates at the first command that returns code other than 0.')
@click.option('-j', '--jobs', type=int, help='Number of concurent jobs that will execute commands. 0 means `auto`.')
@click.option('-q', '--quiet', is_flag=True, help='Do not print anything except stdout and stderr of the executed commands.')
@click.option('--color', type=click.Choice(['always', 'auto', 'never']), default='auto', help='When to use terminal colors.')
@click.version_option(None, '-V', '--version', package_name='para-cada', prog_name=PROG_NAME)
def main(command_expr, eval_expr, **kwargs):
    """Executes your command for each file selected using glob expression(s)."""
    Runner(command_expr, eval_expr, **kwargs).run()

if __name__ == '__main__':
    main()
