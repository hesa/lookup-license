# SPDX-FileCopyrightText: 2025 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

def get_keypath(data, path):
    inner_data = data
    for sub_path in path.split('.'):
        try:
            inner_data = inner_data[sub_path]
        except Exception:
            return None
    return inner_data

def contains(url, strings):
    res = any(map(url.__contains__, strings))
    return res
