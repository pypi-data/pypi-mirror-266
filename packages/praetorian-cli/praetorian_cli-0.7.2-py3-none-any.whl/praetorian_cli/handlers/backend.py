import os
import click

from praetorian_cli.handlers.utils import chaos
from praetorian_cli.handlers.utils import handle_api_error


@chaos.command('seeds')
@click.pass_obj
@handle_api_error
@click.option('-seed', '--seed', default="", help="Filter by seed domain")
def my_seeds(controller, seed):
    """ Fetch seed domains """
    result = controller.my(dict(key=f'#seed#{seed}'))
    for hit in result.get('seeds', []):
        print(f"{hit['key']}")


@chaos.command('assets')
@click.pass_obj
@handle_api_error
@click.option('-seed', '--seed', default="", help="Filter by seed domain")
def my_assets(controller, seed):
    """ Fetch existing assets """
    result = controller.my(dict(key=f'#asset#{seed}'))
    for hit in result.get('assets', []):
        print(f"{hit['key']}")


@chaos.command('risks')
@click.pass_obj
@handle_api_error
@click.option('-seed', '--seed', default="", help="Filter by seed domain")
def my_risks(controller, seed):
    """ Fetch current risks """
    result = controller.my(dict(key=f'#risk#{seed}'))
    for hit in result.get('risks', []):
        print(f"{hit['key']}")


@chaos.command('jobs')
@click.pass_obj
@handle_api_error
@click.option('-seed', '--seed', default="", help="Filter by seed domain")
def my_jobs(controller, seed):
    """ Fetch past, present and future jobs """
    result = controller.my(dict(key=f'#job#{seed}'))
    for hit in result.get('jobs', []):
        print(f"{hit['key']}")


@chaos.command('services')
@click.pass_obj
@handle_api_error
@click.option('-port', '--port', default="", help="Filter by port")
def my_services(controller, port):
    """ Fetch recently seen services """
    result = controller.my(dict(key=f'#service#{port}'))
    for hit in result.get('services', []):
        print(f"{hit['key']}")


@chaos.command('files')
@click.pass_obj
@handle_api_error
@click.option('-key', '--key', default="", help="Filter by relative path")
def my_files(controller, key):
    """ Fetch all file names """
    result = controller.my(dict(key=f'#file#{key}'))
    for hit in result.get('files', []):
        print(f"{hit['key']}")


@chaos.command('threats')
@click.pass_obj
@handle_api_error
@click.option('-source', '--source', type=click.Choice(['KEV']), default="KEV", help="Filter by threat source")
def my_threats(controller, source):
    """ Fetch threat intelligence """
    result = controller.my(dict(key=f'#threat#{source}'))
    for hit in result.get('threats', []):
        print(f"{hit['key']}")


@chaos.command('add-seed')
@click.pass_obj
@handle_api_error
@click.argument('seed')
@click.option('-comment', '--comment', default="", help="Add a description")
def add_seed(controller, seed, comment):
    """ Add a new seed domain """
    controller.upsert_seed(seed, status=0, comment=comment)


@chaos.command('freeze-seed')
@click.pass_obj
@handle_api_error
@click.argument('seed')
def freeze_seed(controller, seed):
    """ Freeze a seed domain  """
    controller.upsert_seed(seed, 1)


@chaos.command('add-risk')
@click.pass_obj
@handle_api_error
@click.argument('key')
@click.option('-finding', '--finding', required=True, help="Generic risk identifier")
@click.option('-status', '--status', type=click.IntRange(0, 3), required=False, help="Open (0) Closed (1) Rejected (2) Triage (3)")
@click.option('-severity', '--severity', type=click.IntRange(0, 4), required=False, help="Info (0) Med (1) High (2) Critical (3)")
def add_risk(controller, composite, finding, status=0, severity=0):
    """ Apply a risk to an asset key """
    print(controller.add_risk(key, finding, status, severity))


@chaos.command('upload')
@click.pass_obj
@handle_api_error
@click.argument('name')
def upload(controller, name):
    """ Upload a file """
    controller.upload(name)


@chaos.command('download')
@click.pass_obj
@handle_api_error
@click.argument('key')
@click.argument('path')
def download(controller, key, path):
    """ Download any previous uploaded file """
    controller.download(key, path)


@chaos.command('test')
@click.pass_obj
def trigger_all_tests(controller):
    try:
        import pytest
    except ModuleNotFoundError:
        print("Install pytest using 'pip install pytest' to run this command")
    test_directory = os.path.relpath("praetorian_cli/sdk/test", os.getcwd())
    pytest.main([test_directory])
