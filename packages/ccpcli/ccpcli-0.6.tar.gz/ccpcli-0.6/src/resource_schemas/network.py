###############################################################################
# Copyright (c) 2024-present CorEdge India Pvt. Ltd - All Rights Reserved     #
# Unauthorized copying of this file, via any medium is strictly prohibited    #
# Proprietary and confidential                                                #
# Written by Mani Keshari <mani@coredge.io>, April 2024                       #
###############################################################################
from src.util.utils import get_nested_value, convert_unix_timestamp


def network_list_response(res):
    """This function is preparing response keys for listing networks in tabular view.
    Update the response keys to match the table header for listing networks.


    Args:
        res (dict or list): The original response containing network information.

    Returns:
        dict or list: The updated response with keys renamed according to the table header.
    """
    for r in res:
        r['subnet_name'] = get_nested_value(r, ['subnet_network',0, 'subnet_name'])
        r['network_address'] = get_nested_value(r, ['subnet_network',0, 'network_address'])
        r['ip_version'] = get_nested_value(r, ['subnet_network',0, 'ip_version'])
        r['gateway_ip'] = get_nested_value(r, ['subnet_network',0, 'gateway_ip'])
        r['created_at'] = convert_unix_timestamp(r['created'])
    return res


def network_describe_response(res):
    """ This function is preparing response keys for showing network in tabular view.
    Update the response keys to match the table header for retrieving a network.

        Args:
            res (dict): The original response containing network information.

        Returns:
            dict: The updated response with keys renamed according to the table header.
        """
    res['subnet_name'] = get_nested_value(res, ['subnet_network',0, 'subnet_name'])
    res['network_address'] = get_nested_value(res, ['subnet_network',0, 'network_address'])
    res['ip_version'] = get_nested_value(res, ['subnet_network',0, 'ip_version'])
    res['gateway_ip'] = get_nested_value(res, ['subnet_network',0, 'gateway_ip'])
    res['created_at'] = convert_unix_timestamp(res['created'])
    return res


def security_group_list_response(res):
    """This function is preparing response keys for listing security groups in tabular view.
    Update the response keys to match the table header for listing security groups.


    Args:
        res (dict or list): The original response containing security group information.

    Returns:
        dict or list: The updated response with keys renamed according to the table header.
    """
    for r in res:
        r['created_at'] = convert_unix_timestamp(r['created'])
        r['last_updated_at'] = convert_unix_timestamp(r['updated'])
        r['type'] = r['security_group_type']
    return res