# Copyright (c) 2024 Henix, Henix.fr
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""opentf-ctl datasources handling part"""

from typing import Any, Dict, List

import sys

from opentf.tools.ctlcommons import (
    _debug,
    _is_command,
    _error,
    _ensure_options,
    _ensure_uuid,
    _fatal,
    generate_output,
    _get_arg,
    _make_params_from_selectors,
)
from opentf.tools.ctlconfig import read_configuration
from opentf.tools.ctlnetworking import _observer, _get
from opentf.tools.ctlworkflows import _get_workflows

#######################################################################
# Help messages

GET_DATASOURCES_HELP = '''Get workflow datasources

Example:
  # Get workflow testcases datasource
  opentf-ctl get b0dcc5e2-c905-4608-9177-7ea7e50827e0 datasources --kind=testcases

Options:
  --kind=kind or -k kind: get datasources of specified kind (mandatory)
  --output=format or -o format: show information in specified format (json or yaml).
    (more at: https://opentestfactory.org/tools/running-commands#output-formats)
  --output=wide or -o wide: show additional information (environment tags and job name).
  --output=custom-columns= or -o custom-columns=: show specified information.
    (more at: https://opentestfactory.org/tools/running-commands#output-formats)
  --field-selector=s: selector (field query) to filter on, supports '=', '==', and '!='. (e.g. --field-selector key1=value1,key2=value2)
    (more at: https://opentestfactory.org/tools/running-commands#label-and-field-selectors)

Usage:
  opentf-ctl get WORKFLOW_ID datasources [--kind=kind] [options]

Use "opentf-ctl options" for a list of global command-line options (applies to all commands).
'''

#######################################################################
# Constants

DEFAULT_COLUMNS = (
    'NAME:.name',
    'TECHNOLOGY:.test.technology',
    'STATUS:.test.status',
    'EXECUTION TIME:.duration',
)

WIDE_COLUMNS = (
    'NAME:.name',
    'TECHNOLOGY:.test.technology',
    'STATUS:.test.status',
    'EXECUTION TIME:.duration',
    'RUNS-ON:.test.runs-on',
    'JOB:.test.job',
)

#######################################################################


def _query_observer_datasources(
    workflow_id: str, datasources_kind: str
) -> List[Dict[str, Any]]:
    url = f'/workflows/{workflow_id}/datasources/{datasources_kind}'
    response = _get(
        _observer(),
        url,
        'Could not get datasources.',
        params=_make_params_from_selectors(),
        statuses=(200, 204, 404, 422),
        raw=True,
    )

    if response.status_code == 200 and not response.json()['details'].get('items'):
        print(response.json()['message'])
        sys.exit(0)

    try:
        items = response.json()['details']['items']
        while 'next' in response.links:
            next_url = url + '?' + response.links['next']['url'].partition('?')[2]
            response = _get(
                _observer(),
                next_url,
                'Could not get datasources.',
                statuses=(200, 204, 404, 422),
                raw=True,
            )
            items += response.json()['details']['items']
        return items
    except ValueError as err:
        _error('Could not deserialize observer response: %s.', str(err))
        _debug(response.text)
        sys.exit(2)


def get_datasources(workflow_id: str):
    workflow_id = _ensure_uuid(workflow_id, _get_workflows)
    datasources_kind = _get_arg('--kind=') or _get_arg('--k=')
    if not datasources_kind:
        _error('No datasources kind provided.')
        sys.exit(1)
    try:
        datasources = _query_observer_datasources(workflow_id, datasources_kind)
        generate_output(datasources, DEFAULT_COLUMNS, WIDE_COLUMNS)
    except Exception as err:
        _fatal(
            'Failed to get %s datasources for workflow %s: %s.',
            datasources_kind,
            workflow_id,
            str(err),
        )


#######################################################################
# Exposed functions


def print_get_datasources_help(args: List[str]):
    """Display help."""
    if _is_command('get datasources', args):
        print(GET_DATASOURCES_HELP)
    else:
        _error('Unknown command.  Use --help to list known commands.')
        sys.exit(1)


def get_datasources_cmd():
    """Get workflow datasources."""
    if _is_command('get _ datasources', sys.argv):
        workflow_id = _ensure_options(
            'get _ datasources',
            sys.argv[1:],
            extra=[
                ('--field-selector',),
                ('--output', '-o'),
                ('--kind', '-k'),
            ],
        )
        read_configuration()
        get_datasources(workflow_id)  # type: ignore
    else:
        _error('Unknown command.  Use --help to list known commands.')
        sys.exit(1)
