# -*- coding: utf-8 -*-
# Copyright (c) 2020, René Moser <mail@renemoser.net>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):

    # Standard cloudstack documentation fragment
    DOCUMENTATION = '''
options:
  api_token:
    description:
      - API token.
      - This can also be passed in the C(PINGPING_API_TOKEN) environment variable.
    required: true
    type: str
  api_timeout:
    description:
      - Timeout in seconds API.
    default: 30
    type: int
notes:
  - "For details consult the full API documentation: U(https://docs.pingping.io)."
'''
