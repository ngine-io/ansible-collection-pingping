![Collection integration](https://github.com/ngine-io/ansible-collection-pingping/workflows/Collection%20integration/badge.svg)
 [![Codecov](https://img.shields.io/codecov/c/github/ngine-io/ansible-collection-pingping)](https://codecov.io/gh/ngine-io/ansible-collection-pingping)
[![License](https://img.shields.io/badge/license-GPL%20v3.0-brightgreen.svg)](LICENSE)

# Ansible Collection for pingping.io

This collection provides a series of Ansible modules and plugins for interacting with [pingping.io](https://www.pingping.io) monitoring service.

## Requirements

- ansible version >= 2.9

## Installation

To install the collection hosted in Galaxy:

```bash
ansible-galaxy collection install ngine_io.pingping
```

To upgrade to the latest version of the collection:

```bash
ansible-galaxy collection install ngine_io.pingping --force
```

## Usage

### Playbooks

To use a module from pingping.io collection, please reference the full namespace, collection name, and modules name that you want to use:

```yaml
---
- name: Using pingping.io collection
  hosts: localhost
  tasks:
    - ngine_io.pingping.monitor:
        name: web1
        url: ...
        api_token: ...
```

Or you can add full namepsace and collecton name in the `collections` element:

```yaml
---
- name: Using pingping.io collection
  hosts: localhost
  collections:
    - ngine_io.pingping
  tasks:
    - monitor:
        name: web1
        url: ...
        api_token: ...
```

## Contributing

There are many ways in which you can participate in the project, for example:

- Submit bugs and feature requests, and help us verify as they are checked in
- Review source code changes
- Review the documentation and make pull requests for anything from typos to new content
- If you are interested in fixing issues and contributing directly to the code base, please see the [CONTRIBUTING](CONTRIBUTING.md) document.

## License

GNU General Public License v3.0

See [COPYING](COPYING) to see the full text.
