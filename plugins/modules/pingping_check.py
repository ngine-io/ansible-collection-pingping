#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2020, René Moser <mail@renemoser.net>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: pingping_check
short_description: Manages monitor checks on pingping.io
description:
  - Enable, update and disable monitor checks.
author:
  - René Moser (@resmo)
version_added: "1.0"
options:
  name:
    description:
      - Type of the check to be modified.
    type: str
    choices:
      - certificate_health
      - uptime
    required: true
  monitor:
    description:
      - Name of the monitor, the check is related to.
    type: str
    required: true
  interval:
    description:
      - Interval the check should be executed in seconds.
    type: int
  notification_threshold:
    description:
      - Notification threshold in secodns.
      - Idempotency is not possible due to API limitation, change also I(interval) to change I(notification_threshold).
    type: int
  state:
    description:
      - State of the check.
    choices:
      - disabled
      - enabled
    default: enabled
    type: str
extends_documentation_fragment: ngine_io.pingping.pingping
'''

EXAMPLES = '''
---
- name: Increase interval for uptime check
  pingping_check:
    name: uptime
    monitor: my-name
    # 15 minutes
    interval: 900
    # immediately
    notification_threshold: 0
    api_token: xxxxxx

- name: Set interval and notification threshold for certificates health check
  pingping_check:
    name: certificate_health
    monitor: my-name
    # 1/2 day
    interval: 43200
    # 14 days
    notification_threshold: 1209600
    api_token: xxxxxx

- name: Disable the certificates health check
  pingping_check:
    name: certificate_health
    monitor: my-name
    state: disabled
    api_token: xxxxxx
'''

RETURN = '''
---
pingping_check:
  description: Response from Pingping API
  returned: success
  type: complex
  contains:
    id:
      description: ID of the check
      returned: success
      type: int
      sample: 55471
    interval:
      description: Interval of the check
      returned: success
      type: int
      sample: 900
    is_enabled:
      description: Whether the check is enabled or not
      returned: success
      type: bool
      sample: true
    last_check_at:
      description: Whether the check is enabled or not
      returned: success
      type: str
      sample: "2020-05-17 20:59:38"
    meta:
      description: Whether the check is enabled or not
      returned: success
      type: dict
      sample: {"average_response_time": null, "average_uptime_percentage": null, "http_status_code": null, "offline_since": null}
    monitor:
      description: Monitor the check is related to
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
    name:
      description: Name of the check
      returned: success
      type: str
      sample: uptime
    status:
      description: Status of the check
      returned: success
      type: str
      sample: ok
    error:
      description: Error of the check
      returned: success
      type: str
      sample: none
'''

from ansible.module_utils._text import to_text
from ansible.module_utils.six.moves.urllib.parse import urlparse, parse_qs, unquote_plus
from ansible.module_utils.basic import AnsibleModule
from ..module_utils.pingping import (
    AnsiblePingpingBase,
    pingping_argument_spec,
)


class AnsiblePingpingCheck(AnsiblePingpingBase):

    def __init__(self, module):
        super(AnsiblePingpingCheck, self).__init__(module)
        self.namespace = "pingping_check"

    def _is_diff(self, data, check):
        is_diff = False
        check_element_keys = ['interval', ]
        for key in check_element_keys:
            if data.get(key) is None:
                continue
            if data[key] != check[key]:
                is_diff = True
        return is_diff

    def _update_check(self, check):
        interval = self._module.params.get('interval')
        notification_threshold = self._module.params.get('notification_threshold')
        if interval is None and notification_threshold is None:
            return check

        data = {
            'interval': interval,
            'notification_threshold': notification_threshold,
        }

        if self._is_diff(data, check):
            self._result['changed'] = True

            self._result['diff']['after'].update(data)

            if not self._module.check_mode:
                self._put('checks/%s' % check['id'], data)

        return check

    def _enable_disable_check(self, check):
        state = self._module.params.get('state')
        check_state = "enabled" if check['is_enabled'] else "disabled"

        if state != check_state:
            self._result['changed'] = True
            self._result['diff']['after'].update({
                'is_enabled': not check['is_enabled'],
            })
            if not self._module.check_mode:
                if check['is_enabled']:
                    action = "disable"
                else:
                    action = "enable"
                self._post("checks/%s/%s" % (check['id'], action))

        return check

    def get_monitor(self):
        name = self._module.params.get('monitor')
        matching_monitors = []
        res = self._get('monitors')
        for monitor in res.get('data') or []:
            if monitor['alias'] == name:
                matching_monitors.append(monitor)

        if len(matching_monitors) > 1:
            self._module.fail_json(
                msg="More than one monitor with name exists: %s" % name)
        elif len(matching_monitors) == 1:
            return matching_monitors[0]

        self._module.fail_json(msg="No matching monitor found: %s" % name)

    def _get_check(self):
        monitor = self.get_monitor()
        name = self._module.params.get('name')
        check = monitor.get('checks').get(name)

        check.update({
            'name': name,
            'monitor': {
                'id': monitor['id'],
                'alias': monitor['alias'],
            }
        })

        self._result['diff']['before'] = check.copy()
        self._result['diff']['after'] = check.copy()

        return check

    def present(self):
        check = self._get_check()
        check = self._update_check(check)
        check = self._enable_disable_check(check)
        if self._result['changed'] and not self._module.check_mode:
            check = self._get_check()
        return self._transform_result(check)


def main():
    argument_spec = pingping_argument_spec()
    argument_spec.update(dict(
        name=dict(type='str', required=True, choices=['uptime', 'certificate_health']),
        monitor=dict(type='str', required=True),
        interval=dict(type='int'),
        notification_threshold=dict(type='int'),
        state=dict(type='str', choices=['disabled', 'enabled'], default='enabled'),
    ))

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_together=(
            ['interval', 'notification_threshold'],
        ),
        supports_check_mode=True,
    )
    ansible_pingping_check = AnsiblePingpingCheck(module)
    result = ansible_pingping_check.present()
    module.exit_json(**result)


if __name__ == '__main__':
    main()
