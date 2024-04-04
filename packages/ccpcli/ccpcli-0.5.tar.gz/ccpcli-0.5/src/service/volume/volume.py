###############################################################################
# Copyright (c) 2024-present CorEdge India Pvt. Ltd - All Rights Reserved     #
# Unauthorized copying of this file, via any medium is strictly prohibited    #
# Proprietary and confidential                                                #
# Written by Deepak Pant <deepakpant@coredge.io>, April 2023                  #
# Modified by Aman Kadhala <aman@coredge.io>, April 2023                      #
###############################################################################
import os

import click
from src.util.constants import Constants
from src.util.http_helper import delete_assert
from src.util.http_helper import get_assert
from src.util.utils import print_cli, print_info
from src.util.utils import set_context
from src.resource_schemas.volume import volume_list_response


@click.group(name=Constants.COMMAND_GROUP_VOLUME)
@click.pass_context
def volumes(ctx):
    """This command will do all the operations on volumes"""
    pass


@volumes.command(name=Constants.COMMAND_GET)
@click.pass_context
@click.option('--output', '-o', help='Supported formats are json,tabular,yaml', required=False)
def get_volume(ctx, output):
    """This command will provide the list of Volume"""

    # set up the configuration details into ctx object
    set_context(ctx)

    url = f'{ctx.obj.get(Constants.CLOUD_BASE_URL)}{os.sep}volumes'
    params = {'include_bootable': False}

    res = get_assert(ctx, url=url, params=params)

    if output == Constants.TABULAR_OUTPUT:
        volumes = volume_list_response(res)
    else:
        volumes = res

    print_cli(msg=volumes, output_format=output,
              headers=Constants.TABLE_HEADER_VOLUME)


@volumes.command(name=Constants.COMMAND_DESCRIBE)
@click.pass_context
@click.argument('volume')
@click.option('--output', '-o', help='Supported formats are json,tabular,yaml', required=False)
def describe_volume(ctx, volume, output):
    """This command will describe volume"""

    # set up the configuration details into ctx object
    set_context(ctx)

    url = f'{ctx.obj.get(Constants.CLOUD_BASE_URL)}{os.sep}volumes{os.sep}{volume}/'
    res = get_assert(ctx, url=url)

    print_cli(msg=[res], output_format=output)


@volumes.command(name=Constants.COMMAND_DELETE)
@click.pass_context
@click.argument('volume')
def delete_volume(ctx, volume):
    """This command will delete network"""

    # set up the configuration details into ctx object
    set_context(ctx)

    url = f'{ctx.obj.get(Constants.CLOUD_BASE_URL)}{os.sep}volumes{os.sep}{volume}/'

    delete_assert(ctx, url=url, expected_response_code=202)

    print_info("Volume deleting in progress.")

