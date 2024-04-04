###############################################################################
# Copyright (c) 2024-present CorEdge India Pvt. Ltd - All Rights Reserved     #
# Unauthorized copying of this file, via any medium is strictly prohibited    #
# Proprietary and confidential                                                #
# Written by Mani Keshari <mani@coredge.io>, April 2024                       #
###############################################################################
from src.util.utils import get_nested_value, convert_unix_timestamp

def instance_list_response(res):
    """This function is preparing response keys for listing instances in tabular view.
    Update the response keys to match the table header for listing instances.

    Args:
        list : The original response containing instance information.

    Returns:
        list: The updated response with keys renamed according to the table header.
    """
    for r in res:
        r['public_ip'] = r['floating_ip']
        r['created_at'] = convert_unix_timestamp(r['created'])
        r['updated_at'] = convert_unix_timestamp(r['updated'])
    return res