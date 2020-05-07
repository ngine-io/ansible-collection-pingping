# -*- coding: utf-8 -*-
#
# Copyright (c) 2020, René Moser <mail@renemoser.net>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from copy import deepcopy
from ansible.module_utils.basic import env_fallback
from ansible.module_utils.urls import fetch_url
from ansible.module_utils._text import to_text

API_URL = 'https://pingping.io/webapi/'


def pingping_argument_spec():
    return dict(
        api_token=dict(fallback=(env_fallback, ['PINGPING_API_TOKEN']),
                       no_log=True,
                       required=True),
        api_timeout=dict(default=30, type='int'),
    )


class AnsiblePingpingBase(object):

    def __init__(self, module):
        self.namespace = "pingping_base"
        self._module = module
        self._headers = {
            'Authorization': 'Bearer %s' % module.params['api_token'],
            'Content-type': 'application/json'
        }
        self._result = {
            'changed': False,
            'diff': dict(before=dict(), after=dict()),
        }

    def _get(self, api_call):
        resp, info = fetch_url(self._module, API_URL + api_call,
                               headers=self._headers,
                               timeout=self._module.params['api_timeout'])

        if info['status'] == 200:
            return self._module.from_json(to_text(resp.read(), errors='surrogate_or_strict'))
        elif info['status'] == 404:
            return None
        else:
            self._module.fail_json(msg='Failure while calling the API with GET for '
                                       '"%s".' % api_call, fetch_url_info=info)

    def _post_or_put(self, api_call, method, data):
        api_endpoint = API_URL + api_call

        if data is not None:
            for k, v in deepcopy(data).items():
                if v is None:
                    del data[k]
            data = self._module.jsonify(data)

        resp, info = fetch_url(self._module,
                               api_endpoint,
                               headers=self._headers,
                               method=method,
                               data=data,
                               timeout=self._module.params['api_timeout'])

        if info['status'] == 200:
            res = resp.read()
            if not res:
                return

            return self._module.from_json(to_text(res, errors='surrogate_or_strict'))

        self._module.fail_json(msg='Failure while calling the API with %s for '
                                   '"%s".' % (method, api_call), fetch_url_info=info)

    def _post(self, api_call, data=None):
        return self._post_or_put(api_call, 'POST', data)

    def _put(self, api_call, data=None):
        return self._post_or_put(api_call, 'PUT', data)

    def _delete(self, api_call):
        resp, info = fetch_url(self._module,
                               API_URL + api_call,
                               headers=self._headers,
                               method='DELETE',
                               timeout=self._module.params['api_timeout'])

        if info['status'] == 200:
            return

        self._module.fail_json(msg='Failure while calling the cloudscale.ch API with DELETE for '
                                   '"%s".' % api_call, fetch_url_info=info)

    def _transform_result(self, resource):
        if resource:
            self._result[self.namespace] = resource
        else:
            self._result[self.namespace] = None
        return self._result
