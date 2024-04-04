###############################################################################
# Copyright (c) 2024-present CorEdge India Pvt. Ltd - All Rights Reserved     #
# Unauthorized copying of this file, via any medium is strictly prohibited    #
# Proprietary and confidential                                                #
# Written by Mani Keshari <mani@coredge.io>, March 2024                       #
###############################################################################
import os

import click
from src.util.constants import Constants, HttpStatus
from src.util.http_helper import get_assert, patch_assert
from src.util.utils import print_cli, print_error, print_info
from src.util.utils import set_context, save_context
from src.resource_schemas.project import project_describe_response


@click.group(name=Constants.COMMAND_GROUP_PROJECT)
@click.pass_context
def project(ctx):
    """This command will do all the operations on project"""
    pass


@project.command(name=Constants.COMMAND_GET)
@click.pass_context
@click.option('--output', '-o', help='Supported formats are json,tabular,yaml', required=False)
def get_project(ctx, output):
    """This command will provide the list of projects"""

    # set up the configuration details into ctx object
    set_context(ctx)
    projects = ctx.obj.get('projects')

    print_cli(msg=projects, output_format=output,
              headers=Constants.TABLE_HEADER_PROJECTS)


@project.command(name=Constants.COMMAND_DESCRIBE)
@click.pass_context
@click.argument('project')
@click.option('--output', '-o', help='Supported formats are json,tabular,yaml', required=False)
def describe_project(ctx, project, output):
    """This command will describe project"""

    # set up the configuration details into ctx object
    set_context(ctx)
    url = f'{ctx.obj.get(Constants.CLOUD_BASE_URL)}{os.sep}organisations{os.sep}' \
          f'{ctx.obj.get(Constants.ORG_ID)}{os.sep}projects{os.sep}{project}'
    res = get_assert(ctx, url=url)

    if output == Constants.TABULAR_OUTPUT:
        projects = project_describe_response(res)
    else:
        projects = res
    print_cli(msg=[projects],
              output_format=output, headers=Constants.TABLE_HEADER_PROJECTS_DESCRIBE)


@project.command(name=Constants.COMMAND_CURRENT)
@click.pass_context
@click.option('--output', '-o', help='Supported formats are json,yaml', required=False)
def current_project(ctx, output):
    """This command will describe the default set Project"""

    # set up the configuration details into ctx object
    set_context(ctx)
    project = ctx.obj.get(Constants.PROJECT_ID)
    url = f'{ctx.obj.get(Constants.CLOUD_BASE_URL)}{os.sep}organisations{os.sep}' \
          f'{ctx.obj.get(Constants.ORG_ID)}{os.sep}projects{os.sep}{project}'
    res = get_assert(ctx, url=url)

    if output == Constants.TABULAR_OUTPUT:
        projects = project_describe_response(res)
    else:
        projects = res
    print_cli(msg=[projects],
              output_format=output, headers=Constants.TABLE_HEADER_PROJECTS_DESCRIBE)


@project.command(name=Constants.COMMAND_SWITCH_PROJECT)
@click.pass_context
@click.argument('project')
def switch_project(ctx, project):
    """This command will switch project, so it can be used in further operations"""

    # set up the configuration details into ctx object

    set_context(ctx)

    projects = ctx.obj.get(Constants.PROJECTS)


    _project = [p for p in projects if str(p.get('id')) == project]

    if _project:
        if _project[0].get('action') != 'success':
            print_error(f"Can not switch project {_project[0].get('name')} because it is in "
                        f"{_project[0].get('action')} state.")
            raise click.exceptions.Exit()
        ctx.obj[Constants.PROJECT_ID] = _project[0].get('id')
        ctx.obj[Constants.PROJECT_NAME] = _project[0].get('name')

        # Reset the context
        save_context(ctx)

        print_info(
            f"Successfully switched to project {_project[0].get('name')}")
    else:
        print_error(f"Project {project} not found.")
        raise click.exceptions.Exit()


@project.command(name=Constants.COMMAND_SET_DEFAULT_PROJECT)
@click.pass_context
@click.argument('project')
def set_default(ctx, project):
    """This command will set the project id into the default context, so it can be used in further operations"""

    set_context(ctx)

    projects = ctx.obj.get(Constants.PROJECTS)
    _project = [p for p in projects if str(p.get('id')) == project]

    """checking project exists or not"""
    if not _project:
        print_error(f"Project {project} not found.")
        raise click.exceptions.Exit()

    """blocking user to set project as default if it is not success"""
    if _project[0].get('action') != 'success':
        print_error(f"Can not set project {_project[0].get('name')} as default because it is in "
                    f"{_project[0].get('action')} state.")
        raise click.exceptions.Exit()

    org_id = ctx.obj.get(Constants.ORG_ID)
    project_name = _project[0].get('name')

    url = f'{ctx.obj.get(Constants.CLOUD_BASE_URL)}{os.sep}organisations{os.sep}{org_id}{os.sep}projects{os.sep}{project}' \
          f'{os.sep}set-default'

    patch_assert(ctx, url=url, expected_response_code=HttpStatus.NO_CONTENT)

    """updating project as default in context object"""
    ctx.obj[Constants.PROJECT_ID] = project
    ctx.obj[Constants.PROJECT_NAME] = project_name
    save_context(ctx)
    print_info(f"Successfully set project {project_name} as default.")
