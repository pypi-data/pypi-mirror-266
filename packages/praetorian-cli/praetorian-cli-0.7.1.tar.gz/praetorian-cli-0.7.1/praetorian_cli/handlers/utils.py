import click

from functools import wraps
from praetorian_cli.sdk.chaos import Chaos

def handle_api_error(func):
    @wraps(func)
    def handler(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            click.secho(e.args[0], fg='red')
    return handler


@click.group()
@click.pass_context
def chaos(ctx):
    """ Chaos API access """
    ctx.obj = Chaos(keychain=ctx.obj)


