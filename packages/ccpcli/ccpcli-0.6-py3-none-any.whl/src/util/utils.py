###############################################################################
# Copyright (c) 2024-present CorEdge India Pvt. Ltd - All Rights Reserved     #
# Unauthorized copying of this file, via any medium is strictly prohibited    #
# Proprietary and confidential                                                #
# Written by Mani Keshari <mani@coredge.io>, March 2024                       #
###############################################################################
import json
import click
import yaml
from click import echo
from click import style
from src.util import file_utils
from src.util.constants import Constants
from tabulate import tabulate
from datetime import datetime


def read_creds():
    try:
        return file_utils.read(Constants.YNTRAA_CREDS_JSON_FILE)
    except Exception:
        print_error(f"You are either not logged in or logged out out already.")
        raise click.exceptions.Exit()


def delete_creds():
    try:
        return file_utils.delete(Constants.YNTRAA_CREDS_JSON_FILE)
    except Exception:
        pass


def write_creds(creds):
    file_utils.write(data=creds, file=Constants.YNTRAA_CREDS_JSON_FILE)


def save_context(ctx):
    write_creds(creds=ctx.obj)


def set_context(ctx):
    ctx.obj = read_creds()


def clear_context():
    delete_creds()


# Print methods


def print_cli(msg: str, headers=None, err: bool = False, output_format: str = Constants.TABULAR_OUTPUT):
    ''' print the message in the CLI Yaml,Tabular'''
    if output_format is None:
        output_format = Constants.JSON_OUTPUT

    if err:
        print_error(msg)

    else:
        if Constants.TABULAR_OUTPUT == output_format:
            print_table(data=msg, headers=headers)
        elif Constants.YAML_OUTPUT == output_format:
            print_yaml(msg)
        elif Constants.SQL_OUTPUT == output_format:
            print_sql(msg)
        else:
            print_json(msg)


def print_yaml(msg: str):
    """Print a YAML message to the console

    Args:
        msg (str): Message to be printed
    """
    print_info(click.style(yaml.dump(msg)))


def print_sql(msg: str):
    """Print a SQL message to the console

    Args:
        msg (str): Message to be printed
    """
    pass


def print_info(msg: str):
    """Print a message to the console

    Args:
        msg (str): Message to be printed
    """
    click.echo(msg)


def print_json(msg: str):
    """Print a JSON message to the console

    Args:
        msg (str): Message to be printed
    """

    pretty_json = json.dumps(msg, indent=4)
    print_info(click.style(pretty_json))


def print_error(msg: str):
    """Print error message to the console

    Args:
        msg (str): error message
        """
    echo(style(msg, fg='red'), err=True, color=True)


def print_table(data, headers=None):
    """ Print tabular to the console

    Args:
        data (list(dict)): list of data
        headers (list(str), optional): list of headers. Defaults to None.
    """
    if data:
        if not headers:
            headers = [key.upper() for key in data[0].keys()]

        converted_data = []
        for row in data:
            converted_data.append([row.get(item.lower()) for item in headers])


        # replace underscore(_) with space
        headers = [item.replace('_', ' ') for item in headers]
        table = tabulate(tabular_data=converted_data,
                         headers=headers, tablefmt="heavy_grid", stralign="center")

        print_info(table)


def get_nested_value(obj, path):
    """
    Get a nested value from an object based on the given path.

    Args:
        obj: The object from which to extract the nested value.
        path: A list of keys representing the path to the desired value.

    Returns:
        The nested value if found, None otherwise.
    """
    if not path:
        return obj

    # Get the first key in the path
    key = path[0]

    # If the object is a dictionary, get the value using the key
    if isinstance(obj, dict):
        if key in obj:
            return get_nested_value(obj[key], path[1:])

    # If the object is a list and the key is an integer, get the value using the index
    elif isinstance(obj, list) and isinstance(key, int):
        if 0 <= key < len(obj):
            return get_nested_value(obj[key], path[1:])

    # If the key is not found or the object is not iterable, return None
    return None


def convert_unix_timestamp(timestamp):
    # Convert Unix timestamp to datetime object
    dt_object = datetime.fromtimestamp(int(timestamp))

    # Format the datetime object as a string
    formatted_date_time = dt_object.strftime('%Y-%m-%d %H:%M:%S')

    return formatted_date_time


