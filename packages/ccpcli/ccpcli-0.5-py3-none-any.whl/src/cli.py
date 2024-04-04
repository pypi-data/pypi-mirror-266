###############################################################################
# Copyright (c) 2024-present CorEdge India Pvt. Ltd - All Rights Reserved     #
# Unauthorized copying of this file, via any medium is strictly prohibited    #
# Proprietary and confidential                                                #
# Written by Mani Keshari <mani@coredge.io>, March 2024                       #
###############################################################################
import json
import os
from json import JSONDecodeError

import click
import requests
import urllib3
from click import echo
from click import style
from src.project import project
from src.service.network.network import networks
from src.service.volume.volume import volumes
from src.service.network.security_group import security_groups
from src.service.compute.instance import instances
from src.util.constants import Constants, HttpStatus, YntraaCreds
from src.util.http_helper import get_assert
from src.util.utils import print_error, convert_unix_timestamp
from src.util.utils import print_info
from src.util.utils import save_context, clear_context

urllib3.disable_warnings()

__CLOUD_API_BASE_PREFIX = 'api/v1'


@click.group()
@click.pass_context
def cli(ctx):
    if not ctx.obj:
        ctx.obj = {}


def setup(ctx):
    try:
        auth_url = YntraaCreds.auth_url
        cloud_url = YntraaCreds.cloud_url
        client_id = YntraaCreds.client_id

        ctx.obj[Constants.AUTH_URL] = auth_url
        ctx.obj[Constants.CLOUD_URL] = cloud_url
        ctx.obj[Constants.CLIENT_ID] = client_id

        if auth_url and cloud_url:
            ctx.obj[Constants.CLOUD_BASE_URL] = f"{cloud_url}{os.sep}{__CLOUD_API_BASE_PREFIX}"
        else:
            echo(style('Missing required configuration parameters. Please contact support for assistance.',
                       fg='red'), err=True, color=True)

    except Exception as e:
        echo(style(
            f'An unexpected error occurred while setting up the configuration. Please try again later or contact support for assistance. Error: {e}',
            fg='red'), err=True, color=True)
        raise click.exceptions.Exit()


def get_access_token(ctx, username, password):
    payload = {'username': username, 'password': password, 'grant_type': Constants.GRANT_TYPE,
               'client_id': ctx.obj.get(Constants.CLIENT_ID),
               }

    headers = {Constants.CONTENT_TYPE: Constants.APPLICATION_FORM_TYPE}
    url = f'{ctx.obj.get(Constants.AUTH_URL)}{os.sep}realms{os.sep}myaccount{os.sep}protocol' \
          f'{os.sep}openid-connect{os.sep}token'

    try:
        response = requests.post(
            url=url, data=payload, headers=headers, verify=False)

        if response.status_code == HttpStatus.OK:
            return response.json()['access_token']
        else:
            raise Exception(response.json()['error_description'])
    except Exception as e:
        print_error(e)
        raise click.exceptions.Exit()


@cli.command()
@click.pass_context
def login(ctx):
    """ login to cloud console """

    username = click.prompt('Username')

    # Prompt for the password without displaying it
    password = click.prompt('Password', hide_input=True)

    # set up the configuration
    setup(ctx)

    """login to the yntraa """
    access_token = get_access_token(
        ctx, username, password)

    # Add user details in the context
    ctx.obj[Constants.ACCESS_TOKEN] = access_token

    # Call web sso to get user's details

    """Fetching organisation details and user details"""
    url = f'{ctx.obj.get(Constants.CLOUD_BASE_URL)}{os.sep}users{os.sep}me'
    user_details = get_assert(ctx, url=url)

    user_id = user_details.get('id')
    name = user_details.get('first_name')
    email = user_details.get('email')

    org = user_details.get('organisation_project_user_user')[0].get('organisation')
    org_id = org['id']
    org_name = org['name']

    ctx.obj[Constants.NAME] = name
    ctx.obj[Constants.EMAIL] = email
    ctx.obj[Constants.ORG_ID] = org_id
    ctx.obj[Constants.ORG_NAME] = org_name

    """checking current default project for the current user"""
    url = f'{ctx.obj.get(Constants.CLOUD_BASE_URL)}{os.sep}organisations{os.sep}{org_id}{os.sep}users{os.sep}{user_id}{os.sep}project-roles'
    project_roles = get_assert(ctx, url=url)

    projects = []
    for obj in project_roles:
        project = obj.get('project')
        if obj.get('default'):
            ctx.obj[Constants.PROJECT_ID] = project.get('id')
            ctx.obj[Constants.PROJECT_NAME] = project.get('name')

        projects.append({
            'id': project['id'],
            'name': project['name'],
            'status': project['status'],
            'created_at': convert_unix_timestamp(project['created']),
            'created_by': obj.get('user', {}).get('username'),
            'action': project['action']
        })

    ctx.obj[Constants.PROJECTS] = projects

    # save data in file system
    save_context(ctx)

    print_info(
        f'Welcome {name}!! You are successfully logged into the CCP Cloud Console.')
    print_info(f'Default project is set to {ctx.obj[Constants.PROJECT_NAME]}')


@cli.command()
@click.pass_context
def logout(ctx):
    """ logout from cloud console """
    # ToDo - Add logout functionality. It is for temporary purpose.
    clear_context()
    print_info('You are successfully logged out from the CCP Cloud Console.')


# Add commands to the cli group
cli.add_command(project)
cli.add_command(networks)
cli.add_command(volumes)
cli.add_command(security_groups)
cli.add_command(instances)
