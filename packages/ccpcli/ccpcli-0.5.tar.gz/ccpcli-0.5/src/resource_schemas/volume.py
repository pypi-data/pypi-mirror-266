###############################################################################
# Copyright (c) 2024-present CorEdge India Pvt. Ltd - All Rights Reserved     #
# Unauthorized copying of this file, via any medium is strictly prohibited    #
# Proprietary and confidential                                                #
# Written by Mani Keshari <mani@coredge.io>, March 2024                       #
###############################################################################
from src.util.utils import get_nested_value, convert_unix_timestamp


def volume_list_response(res):
    """This function is preparing response keys for listing volumes in tabular view.
    Update the response keys to match the table header for listing volumes.


    Args:
        res (dict or list): The original response containing volume listing information.

    Returns:
        dict or list: The updated response with keys renamed according to the table header.
    """
    for r in res:
        r['created_at'] = convert_unix_timestamp(r['created'])
        r['volume_type'] = get_nested_value(r, ['volume_type', 'name'])
    return res