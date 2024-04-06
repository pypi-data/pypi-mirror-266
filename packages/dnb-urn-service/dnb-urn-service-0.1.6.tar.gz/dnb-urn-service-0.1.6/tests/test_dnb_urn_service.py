# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 University of Münster.
#
# dnb-urn-service is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Tests for /urns/urn POST."""

import random
import sys

import pytest
from helpers import get_client, get_credentials

from dnb_urn_service.errors import (
    DNBURNServiceConflictError,
    DNBURNServiceUrnNotRegisteredError,
    DNBURNServiceUserNotAuthorizedError,
)


def test_urn_post():
    """Test."""
    username, password, prefix = get_credentials()
    d = get_client(username=username, password=password, prefix=prefix)
    i = None
    result = 200
    while result == 200:
        i = random.randint(1, sys.maxsize)
        try:
            result = d.check_if_registered("urn:nbn:de:hbz:6-" + str(i))
        except DNBURNServiceUrnNotRegisteredError:
            result = 404
    result = d.create_urn(
        "https://test.org/" + str(i) + ".pdf", "urn:nbn:de:hbz:6-" + str(i)
    )
    assert result == "urn:nbn:de:hbz:6-" + str(i)


def test_urn_get_403():
    """Test."""
    username, password, prefix = get_credentials()
    d = get_client(username="username", password="password", prefix=prefix)
    with pytest.raises(DNBURNServiceUserNotAuthorizedError):
        d.get_urn("urn:nbn:de:hbz:6-1")


def test_urn_get_404():
    """Test."""
    username, password, prefix = get_credentials()
    d = get_client(username=username, password=password, prefix=prefix)
    with pytest.raises(DNBURNServiceUrnNotRegisteredError):
        d.get_urn("urn:nbn:de:hbz:6-123")


def test_urn_post_409():
    """Test."""
    username, password, prefix = get_credentials()
    d = get_client(username=username, password=password, prefix=prefix)
    with pytest.raises(DNBURNServiceConflictError):
        result = d.create_urn("https://test.org/abc.pdf", "urn:nbn:de:hbz:6-1")


def test_urn_delete():
    """Test."""
    username, password, prefix = get_credentials()
    d = get_client(username=username, password=password, prefix=prefix)
    with pytest.raises(DNBURNServiceUserNotAuthorizedError):
        d.delete_urn("urn:nbn:de:hbz:6-1")
