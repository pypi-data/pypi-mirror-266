###############################################################################
# Copyright (c) 2024-present CorEdge India Pvt. Ltd - All Rights Reserved     #
# Unauthorized copying of this file, via any medium is strictly prohibited    #
# Proprietary and confidential                                                #
# Written by Mani Keshari <mani@coredge.io>, March 2024                       #
###############################################################################
import json

import click
from click import echo
from click import style
import os


def read(file):
    try:
        with open(file, 'r') as f:
            return json.load(f)
    except Exception as e:
        raise e


def write(file, data):

    try:
        directory = os.path.dirname(file)
        if not os.path.exists(directory):
            os.makedirs(directory, mode=0o755, exist_ok=True)

        with open(file, 'w+') as f:
            f.truncate(0)  # remove existing content
            json.dump(data, f)

    except PermissionError:
        echo(style(f'Please provide the write permission to given folder {file} ',
                   fg='red'), err=True, color=True)
        raise click.exceptions.Exit()
    except Exception:
        echo(
            style('Error occurred while writing the data into a file. Please check the configuration again.', fg='red'),
            err=True, color=True)
        raise click.exceptions.Exit()


def delete(file):
    try:
        with open(file, 'w') as f:
            f.truncate(0)  # remove existing content
    except Exception as e:
        raise e
