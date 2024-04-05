###############################################################################
# Copyright (c) 2024-present CorEdge India Pvt. Ltd - All Rights Reserved     #
# Unauthorized copying of this file, via any medium is strictly prohibited    #
# Proprietary and confidential                                                #
# Written by Mani Keshari <mani@coredge.io>, April 2024                       #
###############################################################################
from src.util.utils import get_nested_value, convert_unix_timestamp
from src.util.constants import Constants


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


def flavors_list_response(res):
    """This function is preparing response keys for listing flavors in tabular view.
        Update the response keys to match the table header for listing instances.

        Args:
            list : The original response containing flavors information.

        Returns:
            list: The updated response with keys renamed according to the table header.
        """
    for r in res:
        r['flavor_group'] = r.get('flavor_group').get('name')
        r['ram(mb)'] = r.get("ram")
        for price in r.get('prices'):
            if price.get("unit") == Constants.MONTHLY_BILLING_UNIT:
                r["monthly_price(inr)"] = price.get("cost")
            if price.get("unit") == Constants.HOURLY_BILLING_UNIT:
                r["hourly_price(inr)"] = price.get("cost")

    return res


def images_list_response(res):
    """This function is preparing response keys for listing images in tabular view.
            Update the response keys to match the table header for listing images.

            Args:
                list : The original response containing flavors information.

            Returns:
                list: The updated response with keys renamed according to the table header.
            """

    for r in res:
        r["distribution"] = r.get("os_group_label")
        for price in r.get("prices"):
            # In images list we are getting more than 1 MRC/HRC pricing. SOo we are taking only first MRC/HRC product price.
            if price.get("unit") == Constants.HOURLY_BILLING_UNIT:
                if not r.get("hourly_price(inr)"):
                    r["hourly_price(inr)"] = price.get("cost")

            if price.get("unit") == Constants.MONTHLY_BILLING_UNIT:
                if not r.get("monthly_price(inr)"):
                    r["monthly_price(inr)"] = price.get("cost")

    return res