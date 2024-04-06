# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 University of Münster.
#
# invenio-dnb-urn is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio Serializer to create xepicur serialization for DNB harvesting."""

from .provider import DnbUrnProvider
from .serialize import InvenioSerializerXMetaDissPlus

__version__ = "0.2.2"

__all__ = (
    "__version__",
    "InvenioSerializerXMetaDissPlus",
    "DnbUrnProvider",
)
