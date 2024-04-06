# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 University of Münster.
#
# invenio-dnb-urn is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Module tests."""


def test_version():
    """Test version import."""
    from invenio_dnb_urn import __version__

    assert __version__
