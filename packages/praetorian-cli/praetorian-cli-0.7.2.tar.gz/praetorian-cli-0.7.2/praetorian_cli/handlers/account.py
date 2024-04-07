import click
import random

from utils import chaos
from utils import handle_api_error
from base64 import b64encode
from praetorian_cli.sdk.keychain import verify_credentials


@chaos.command('accounts')
@click.pass_obj
@handle_api_error
def my_accounts(controller):
    """ Fetch my associated accounts """
    result = controller.my(dict(key=f'#account'))
    for hit in result.get('accounts', []):
        print(f"{hit['key']}")


@chaos.command('link-account')
@click.pass_obj
@handle_api_error
@click.argument('username')
def link_account(controller, username, secret):
    """ Link another Chaos account to yours """
    result = controller.link_account(username=username, config='')
    print(f"{result['key']}")


@chaos.command('unlink-account')
@click.pass_obj
@handle_api_error
@click.argument('username')
def unlink_account(controller, username):
    """ Unlink a Chaos account from yours """
    result = controller.unlink_account(username=username)
    print(f"{result['key']}")


@chaos.command('add-webhook')
@click.pass_obj
@handle_api_error
@verify_credentials
def add_webhook(controller):
    """ Create a webhook for adding assets and risks """
    pin = str(random.randint(10000, 99999))
    username = b64encode(controller.keychain.username.encode('utf8'))
    encoded_string = username.decode('utf8')
    encoded_username = encoded_string.rstrip('=')

    controller.link_account(username="hook", config=pin)
    print(f'{controller.keychain.api}/hook/{encoded_username}/{pin}')


@chaos.command('integrate-slack')
@click.pass_obj
@handle_api_error
@click.argument('webhook')
def integrate_slack(controller, webhook):
    controller.link_account('slack', webhook)


@chaos.command('integrate-jira')
@click.pass_obj
@handle_api_error
@click.argument('domain')
@click.argument('access_token')
@click.argument('project_key')
@click.argument('issue_type_id')
def integrate_jira(controller, domain, access_token, project_key, issue_type_id):
    config = {'domain': domain, 'accessToken': access_token, 'projectKey': project_key, 'issueId': issue_type_id}
    controller.link_account('jira', config)
