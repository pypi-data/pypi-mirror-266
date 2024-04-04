###############################################################################
# Copyright (c) 2024-present CorEdge India Pvt. Ltd - All Rights Reserved     #
# Unauthorized copying of this file, via any medium is strictly prohibited    #
# Proprietary and confidential                                                #
# Written by Mani Keshari <mani@coredge.io>, April 2024                       #
###############################################################################
import os

import click
from src.util.constants import Constants
from src.util.http_helper import delete_assert
from src.util.http_helper import get_assert
from src.util.utils import print_cli, print_info
from src.util.utils import set_context
from src.resource_schemas.network import security_group_list_response


@click.group(name=Constants.COMMAND_GROUP_SECURITY_GROUP)
@click.pass_context
def security_groups(ctx):
    """This command will do all the operations on security groups"""
    pass


@security_groups.command(name=Constants.COMMAND_GET)
@click.pass_context
@click.option('--output', '-o', help='Supported formats are json,yaml,tabular', required=False)
def get_security_groups(ctx, output):
    """This command will provide the list of security groups"""
    set_context(ctx)

    url = f'{ctx.obj.get(Constants.CLOUD_BASE_URL)}{os.sep}networks{os.sep}securitygroup{os.sep}'
    res = get_assert(ctx, url=url)

    if output == Constants.TABULAR_OUTPUT:
        security_group_list = security_group_list_response(res)
    else:
        security_group_list = res
    print_cli(msg=security_group_list, output_format=output, headers=Constants.SECURITY_GROUP_TABLE_HEADERS)


