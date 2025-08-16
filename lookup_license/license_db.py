# SPDX-FileCopyrightText: 2025 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

from flame.license_db import FossLicenses # noqa: I900
from flame.license_db import Validation # noqa: I900

class LicenseDatabase:

    fl = FossLicenses()

    @staticmethod
    def expression_license(expr):
        return LicenseDatabase.fl.expression_license(expr, update_dual=False)

    @staticmethod
    def expression_license_identified(expr):
        return LicenseDatabase.fl.expression_license(expr, update_dual=False)['identified_license']

    @staticmethod
    def summarize_license(licenses):
        __licenses = []
        for lic in list(set(licenses)):
            normalized = LicenseDatabase.expression_license_identified(lic)
            __licenses.append(f' ( {normalized} ) ')
        __licenses_string = ' AND '.join(__licenses)
        return str(LicenseDatabase.simplify(__licenses_string))

    @staticmethod
    def simplify(expr):
        if not expr:
            return ''
        return LicenseDatabase.fl.simplify([expr])

    @staticmethod
    def validate(expr):
        return LicenseDatabase.fl.expression_license(expr, validations=[Validation.SPDX], update_dual=False)
