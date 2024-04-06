# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 University of Münster.
#
# dnb-urn-service is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Python API client wrapper for the DNB URN service API."""

from .rest_client import DNBUrnServiceRESTClient

__version__ = "0.1.6"

__all__ = ("__version__", "DNBUrnServiceRESTClient")
