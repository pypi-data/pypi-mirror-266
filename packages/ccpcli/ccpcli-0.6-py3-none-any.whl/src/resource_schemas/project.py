###############################################################################
# Copyright (c) 2024-present CorEdge India Pvt. Ltd - All Rights Reserved     #
# Unauthorized copying of this file, via any medium is strictly prohibited    #
# Proprietary and confidential                                                #
# Written by Mani Keshari <mani@coredge.io>, March 2024                       #
###############################################################################
from src.util.utils import get_nested_value, convert_unix_timestamp


def project_describe_response(res):
    """This function is preparing response keys for describe project in tabular view.
        Update the response keys to match the table header for describe project.


        Args:
            res (dict): The original response containing project information.

        Returns:
            dict: The updated response with keys renamed according to the table header.
        """
    res['organisation_name'] = get_nested_value(res, ['organisation', 'name'])
    res['created_at'] = convert_unix_timestamp(res['created'])
    res['created_by'] = get_nested_value(res, ['user', 'username'])
    res['action'] = res['action']
    return res