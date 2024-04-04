###############################################################################
# Copyright (c) 2024-present CorEdge India Pvt. Ltd - All Rights Reserved     #
# Unauthorized copying of this file, via any medium is strictly prohibited    #
# Proprietary and confidential                                                #
# Written by Mani Keshari <mani@coredge.io>, March 2024                       #
###############################################################################
import os
profile = os.getenv('YNTRAA_CLI_PROFILE', 'dev')
ENV_DEV_FILE_PATH = os.path.join(
    os.getcwd() + os.sep, 'resources', f'env-{profile}')


def read_properties(property_file_path):
    ''' read properties of environment property_file_path and returning dict '''
    try:
        with open(property_file_path, 'r') as f:
            data = f.read()
            commands_dict = {}
            for line in data.split("\n"):
                if line.strip() != "":
                    key, value = line.split("=")
                    commands_dict[key.strip()] = value.strip()
            return commands_dict
    except Exception as e:
        raise e

def replace_field(field_list, field_to_replace, replacement_field):
    """
    Replace a field with a given replacement field in a list of fields.

    Args:
        field_list (list): List of field names.
        field_to_replace (str): Field to be replaced.
        replacement_field (str): Replacement field.

    Returns:
        list: List with the replacement applied.
    """
    return [replacement_field if field == field_to_replace else field for field in field_list]

class Constants(object):
    """Header for CCP"""
    CLIENT_ID: str = 'client-id'
    CLOUD_ID: str = 'cloud-id'
    CLIENT_SECRET: str = 'client-secret'
    ORG_ID: str = 'organisation-id'
    PROJECT_ID: str = 'project-id'
    ACCESS_TOKEN: str = 'access-token'
    ORG_NAME: str = 'org-name'
    PROJECT_NAME: str = 'project-name'
    EMAIL: str = 'email'
    NAME: str = 'name'
    PROJECTS: str = 'projects'

    CLOUD_URL = 'cloud_url'
    AUTH_URL = 'auth_url'
    CLOUD_BASE_URL = 'cloud-base-url'


    # Headers
    PASSWORD_GRANT_TYPE: str = 'password'
    HEADERS_AUTHORIZATION_KEY: str = 'Authorization'
    HEADERS_TOKEN_TYPE: str = 'Bearer'
    CONTENT_TYPE: str = 'Content-Type'
    APPLICATION_FORM_TYPE: str = 'application/x-www-form-urlencoded'
    APPLICATION_JSON_TYPE: str = 'application/json'

    # Output Format
    TABULAR_OUTPUT: str = 'tabular'
    JSON_OUTPUT: str = 'json'
    YAML_OUTPUT: str = 'yaml'
    SQL_OUTPUT: str = 'sql'

    # Files
    YNTRAA_CREDS_JSON_FILE = os.path.join(os.sep, 'tmp', 'ccp', 'ccp.creds')

    COMMON_TABLE_HEADERS = ["ID", "NAME", "STATUS", "CREATED_AT", "CREATED_BY", "LABELS"]

    # Project Table Headers
    TABLE_HEADER_PROJECTS = COMMON_TABLE_HEADERS + ["ACTION"]
    TABLE_HEADER_PROJECTS_DESCRIBE = COMMON_TABLE_HEADERS + ["ORGANISATION_ID", "ORGANISATION_NAME", "ACTION"]

    # Network Table Headers
    TABLE_HEADER_NETWORKS = replace_field(COMMON_TABLE_HEADERS, "NAME", "NETWORK_NAME") + ["MANAGED_BY"]
    TABLE_HEADER_NETWORK_DESCRIBE = TABLE_HEADER_NETWORKS + ["SUBNET_NAME", "NETWORK_ADDRESS", "GATEWAY_IP", "IP_VERSION"]

    # Volume Table Headers
    TABLE_HEADER_VOLUME = replace_field(COMMON_TABLE_HEADERS, "NAME", "VOLUME_NAME") + ["VOLUME_TYPE"]

    # Security Group Table Headers
    SECURITY_GROUP_TABLE_HEADERS = replace_field(COMMON_TABLE_HEADERS, "NAME", "SECURITY_GROUP_NAME") + [
        "TYPE", "MANAGED_BY", "LAST_UPDATED_AT"]

    # Instance Table Headers
    INSTANCE_TABLE_HEADERS = replace_field(COMMON_TABLE_HEADERS, "NAME", "INSTANCE_NAME") + [
        "ACTION", "PRIVATE_IP", "PUBLIC_IP", "UPDATED_AT" ]

    TABLE_HEADER_INSTANCE = ["ID", "NAME", " PUBLIC_V4", "AVAILABILITY_ZONE", "STATUS", "TAGS",
                             "CREATED_BY", "CREATED_AT"]

    # properties = read_properties(ENV_DEV_FILE_PATH)
    GRANT_TYPE = 'password'

    # Cloud CLI Group Command
    # COMMAND_GROUP_PROJECT = properties.get('COMMAND_GROUP_PROJECT')
    # COMMAND_GROUP_NETWORK = properties.get('COMMAND_GROUP_NETWORK')
    # COMMAND_GROUP_VOLUME = properties.get('COMMAND_GROUP_VOLUME')
    # COMMAND_GROUP_INSTANCE = properties.get('COMMAND_GROUP_INSTANCE')
    # COMMAND_GROUP_SECURITY_GROUP = properties.get('COMMAND_GROUP_SECURITY_GROUP')

    COMMAND_GROUP_PROJECT = "projects"
    COMMAND_GROUP_NETWORK = "networks"
    COMMAND_GROUP_VOLUME = "volumes"
    COMMAND_GROUP_INSTANCE = "instances"
    COMMAND_GROUP_SECURITY_GROUP = "security-groups"

    # Cloud CLI Commands
    COMMAND_GET = 'get'
    COMMAND_DESCRIBE = 'describe'
    COMMAND_CREATE = 'create'
    COMMAND_DELETE = 'delete'
    COMMAND_CURRENT = 'current'
    COMMAND_SWITCH_PROJECT = 'switch-project'
    COMMAND_SET_DEFAULT_PROJECT = 'set-default-project'


class HttpStatus:
    # Status Codes
    OK: int = 200
    CREATED: int = 201
    BAD_REQUEST: int = 400
    UNAUTHORIZED: int = 401
    NO_CONTENT: int = 204
    NOT_FOUND: int = 404
    INTERNAL_SERVER_ERROR: int = 500


class YntraaCreds:
    auth_url = "https://uatidpcloud.yotta.com"
    cloud_url = "https://console-revamp-sbx.yntraa.com"
    client_id = "yotta-cli-client"

