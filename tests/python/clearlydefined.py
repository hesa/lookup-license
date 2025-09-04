#!/bin/env python3

# SPDX-FileCopyrightText: 2025 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import pytest

from lookup_license.lookupurl.clearlydefined import Clearlydefined

cd = Clearlydefined()

def test_parameters_pypi():
    pkg_type = 'pypi'
    pkg_namespace = ''
    
    coord_url = cd.parameters_to_coordinate_url(pkg_type, pkg_namespace, pkg_name, pkg_version)

