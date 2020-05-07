#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2020, René Moser <mail@renemoser.net>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: pingping_monitor
short_description: Manages monitors on pingping.io
description:
  - Create, update and remove monitors.
author:
  - René Moser (@resmo)
version_added: "1.0"
options:
  name:
    description:
      - Name (alias) of the monitor.
      - Required if I(state=present).
      - Required either I(name) or I(id).
    type: str
    aliases:
      - alias
  id:
    description:
      - ID of the monitor.
      - Required either I(name) or I(id)
    type: int
  url:
    description:
      - URL to monitor.
      - Required if I(state=present).
    type: str
  state:
    description:
      - State of the monitor.
    choices:
      - absent
      - present
    default: present
    type: str
extends_documentation_fragment: ngine_io.pingping.pingping
'''

EXAMPLES = '''
---
- name: Ensure a monitor exists
  pingping_monitor:
    name: my-name
    url: https://www.example.com
    api_token: xxxxxx

- name: Ensure a monitor exists with modified checks
  pingping_monitor:
    name: my-name
    url: https://www.example.com
    api_token: xxxxxx

- name: Ensure a monitor with ID has expected name
  pingping_monitor:
    id: 123
    name: my-name
    url: https://www.example.com
    api_token: xxxxxx

- name: Ensure a monitor by name is absent
  pingping_monitor:
    name: my-name
    state: absent
    api_token: xxxxxx

- name: Ensure a monitor by id is absent
  pingping_monitor:
    id: 123
    state: absent
    api_token: xxxxxx
'''

RETURN = '''
---
pingping_monitor:
  description: Response from Pingping API
  returned: success
  type: complex
  contains:
    id:
      description: ID of the monitor
      returned: success
      type: int
      sample: 27736
    alias:
      description: Alias of the monitor
      returned: success
      type: int
      sample: "my monitor"
    host:
      description: Host of the URL
      returned: success
      type: str
      sample: example.com
    identifier:
      description: Identifier to monitor
      returned: success
      type: str
      sample: MNhCfPrb
    port:
      description: Port of the URL
      returned: success
      type: str
      sample: ""
    scheme:
      description: Schme of the URL
      returned: success
      type: str
      sample: https
    status_page:
      description: Status Page of the monitor
      returned: success
      type: str
      sample: https://pingping.io/MNhCfPrb
    url:
      description: URL of the monitor
      returned: success
      type: str
      sample: https://example.com?foo=
    checks:
      description: Checks of the monitor
      returned: success
      type: dict
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six.moves.urllib.parse import urlparse, parse_qs, unquote_plus
from ansible.module_utils._text import to_text
from ..module_utils.pingping import (
    AnsiblePingpingBase,
    pingping_argument_spec,
)
from copy import deepcopy


class Url(object):
    '''
    A url object that can be compared with other url orbjects
    without regard to the vagaries of encoding, escaping, and ordering
    of parameters in query strings.
    '''

    def __init__(self, url):
        parts = urlparse(url)
        _query = frozenset(parse_qs(parts.query))
        _path = unquote_plus(parts.path)
        self.parts = parts._replace(query=_query, path=_path)

    def __ne__(self, other):
        return self.parts != other.parts

    def __eq__(self, other):
        return self.parts == other.parts

    def __hash__(self):
        return hash(self.parts)


class AnsiblePingpingMonitor(AnsiblePingpingBase):

    def __init__(self, module):
        super(AnsiblePingpingMonitor, self).__init__(module)
        self.namespace = "pingping_monitor"

    def _create(self):
        self._result['changed'] = True
        data = {
            'alias': self._module.params.get('name'),
            'url': self._module.params.get('url'),
        }
        self._result['diff']['after'] = deepcopy(data)

        if not self._module.check_mode:
            return self._post('monitors', data)

    def _update(self, monitor):
        data = {
            'alias': self._module.params.get('name'),
            'url': self._module.params.get('url')
        }
        self._result['diff']['after'] = deepcopy(data)

        for k, v in data.items():
            monitor_value = monitor.get(k)

            self._result['diff']['before'][k] = monitor_value

            if k == 'url':
                if Url(v) != Url(monitor_value):
                    self._result['changed'] = True
            elif monitor_value != v:
                self._result['changed'] = True

        if self._result['changed'] and not self._module.check_mode:
            monitor = self._put('monitors/%s' % monitor['id'], data)
        return monitor

    def get_monitor(self, monitor_id=None):
        monitor_id = self._module.params.get('id') or monitor_id
        if monitor_id is not None:
            return self._get('monitors/%s' % monitor_id)

        name = self._module.params.get('name')
        matching_monitors = []
        res = self._get('monitors')
        for monitor in res.get('data') or []:
            if monitor['alias'] == name:
                matching_monitors.append(monitor)

        if len(matching_monitors) > 1:
            self._module.fail_json(msg="More than one monitor with name exists: %s" % name)
        elif len(matching_monitors) == 1:
            return matching_monitors[0]

    def present(self):
        monitor = self.get_monitor()
        if not monitor:
            monitor = self._create()
        else:
            monitor = self._update(monitor)

        return self._transform_result(monitor)

    def absent(self):
        monitor = self.get_monitor()
        if monitor:
            self._result['changed'] = True
            if not self._module.check_mode:
                self._delete('monitors/%s' % monitor['id'])
        return self._transform_result(monitor)


def main():
    argument_spec = pingping_argument_spec()
    argument_spec.update(dict(
        id=dict(type='int'),
        name=dict(type='str', aliases=['alias']),
        url=dict(type='str'),
        state=dict(type='str', choices=['absent', 'present'], default='present'),
    ))

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_one_of=[('name', 'id')],
        required_if=[('state', 'present', ['url', 'name'])],
        supports_check_mode=True,
    )
    ansible_pingping_monitor = AnsiblePingpingMonitor(module)

    if module.params['state'] == 'absent':
        result = ansible_pingping_monitor.absent()
    else:
        result = ansible_pingping_monitor.present()

    module.exit_json(**result)


if __name__ == '__main__':
    main()
