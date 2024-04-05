###############################################################################
# Copyright (c) 2024-present CorEdge India Pvt. Ltd - All Rights Reserved     #
# Unauthorized copying of this file, via any medium is strictly prohibited    #
# Proprietary and confidential                                                #
# Written by Mani Keshari <mani@coredge.io>, March 2024                       #
###############################################################################
import click
import requests
from halo import Halo
from src.util.constants import Constants
from src.util.utils import print_error

CONNECTION_TIMEOUT_IN_SEC = 300


def populate_headers(ctx, content_type=None):
    # Read the default user creds from the context

    headers = {
        Constants.CONTENT_TYPE: Constants.APPLICATION_FORM_TYPE if content_type is None else content_type,
    }

    access_token = ctx.obj.get(Constants.ACCESS_TOKEN)
    org_id = str(ctx.obj.get(Constants.ORG_ID))
    project_id = str(ctx.obj.get(Constants.PROJECT_ID))

    if access_token:
        headers[Constants.HEADERS_AUTHORIZATION_KEY] = Constants.HEADERS_TOKEN_TYPE + \
            " " + access_token
    else:
        print_error(f"You are either not logged in or logged out out already.")
        raise click.exceptions.Exit()

    if project_id:
        headers[Constants.PROJECT_ID] = project_id
    if org_id:
        headers[Constants.ORG_ID] = org_id

    return headers


def call_assert(ctx, method, url, expected_response_code, headers=None, data=None, json=None, params=None,
                content_type=None):
    _spinner = Halo(text='Loading...', spinner='dots',
                    text_color='green', color='blue')
    _spinner.start()
    try:
        if not headers:
            # auto-populate headers based on context values
            headers = populate_headers(ctx, content_type)

        response = requests.request(method=method, url=url, headers=headers, verify=False,
                                    timeout=CONNECTION_TIMEOUT_IN_SEC, data=data, json=json, params=params)

        if expected_response_code == response.status_code:
            if response.text:
                return response.json()
            else:
                return None
        else:
            raise Exception(response.json().get('message'))

    except Exception as e:
        print_error(str(e))
        raise click.exceptions.Exit()
    finally:
        _spinner.stop()


def get_assert(ctx, url, headers=None, params=None, expected_response_code=200, content_type=None):
    return call_assert(ctx, 'get', url=url, headers=headers, params=params,
                       expected_response_code=expected_response_code, content_type=content_type)


def post_assert(ctx, url, headers=None, data=None, json=None, expected_response_code=201, content_type=None):

    return call_assert(ctx, 'post', url=url, headers=headers, data=data, json=json,
                       expected_response_code=expected_response_code, content_type=content_type)


def put_assert():
    pass


def patch_assert(ctx, url, headers=None, expected_response_code=200, content_type=None):
    return call_assert(ctx, 'patch', url=url, headers=headers, expected_response_code=expected_response_code, content_type=content_type)


def delete_assert(ctx, url, headers=None, expected_response_code=204, content_type=None):
    return call_assert(ctx, 'delete', url=url, headers=headers, expected_response_code=expected_response_code, content_type=content_type)

