# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 University of Münster.
#
# Invenio-Dnb-Urn is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""URN provider for the DNB URN api."""

from .dnburn import DNBUrnClient, DnbUrnProvider

__all__ = (
    "DNBUrnClient",
    "DnbUrnProvider",
)
