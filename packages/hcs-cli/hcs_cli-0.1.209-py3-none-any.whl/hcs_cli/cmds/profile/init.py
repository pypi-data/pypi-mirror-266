"""
Copyright 2023-2023 VMware Inc.
SPDX-License-Identifier: Apache-2.0

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import click
from hcs_core.ctxp import profile, panic
import hcs_cli.support.profile as profile_support


@click.command()
@click.option("--name", "-n", type=str, required=False, help="Name of the profile, if a non-default one is needed.")
@click.option("--dev/--no-dev", type=bool, default=False, help="Initialize default development profiles.")
def init(name: str, dev: bool):
    """Init profile interactively"""

    profile_support.ensure_default_production_profile()

    if name:
        profile.create(name, profile_support.get_default_profile_template())
        print("Create profile: " + profile.file(name))
        print("Use 'hcs profile edit' to check/update.")
        print("Use 'hcs login --help' to complete authentication.")
    elif dev:
        profile_support.ensure_dev_profiles()
        print()
        print("Next step:")
        print("  'hcs profile --help' : to know profile operations.")
        print("  'hcs profile use'    : to swtich profile.")
        print("  'hcs login --help'   : to complete authentication for the current profile.")
    else:
        panic("Specify the target profile name by --name")
