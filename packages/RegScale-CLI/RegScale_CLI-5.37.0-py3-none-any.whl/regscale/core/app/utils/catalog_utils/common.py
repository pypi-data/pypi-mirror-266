#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Enables comparison of catalogs from the master catalog list and the user's RegScale instance """
import json
from urllib.parse import urlparse

import requests

from regscale.core.app.api import Api

api = Api()


def get_new_catalog(url: str) -> dict:
    """
    Function to download a catalog via API call

    :param str url: URL to download the catalog from
    :return: Catalog API response as a dictionary
    :rtype: dict
    """
    # make sure url is stripped
    url = url.strip()
    new_catalog = {}
    try:
        # call curl command to download the catalog
        response = requests.get(url, timeout=60)
        # parse into a dictionary
        new_catalog = response.json()
    except (requests.exceptions.MissingSchema, json.JSONDecodeError, requests.exceptions.RequestException) as ex:
        api.logger.error("Error: %s on Catalog URL: %s", ex, url)
    # return from the function
    return new_catalog


def is_valid_url(url: str) -> bool:
    """
    Function to validate URL

    :param str url: URL to validate
    :return: Whether the URL is valid
    :rtype: bool
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False
