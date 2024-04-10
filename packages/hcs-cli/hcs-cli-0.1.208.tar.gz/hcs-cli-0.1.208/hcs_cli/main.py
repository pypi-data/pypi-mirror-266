#!/usr/bin/env -S python3 -W ignore

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


import sys
import json
import httpx
import click
import os.path as path
import logging

_script_dir = path.abspath(path.join(path.dirname(path.realpath(__file__)), "."))
_module_dir = _script_dir
if __name__ == "__main__":
    _cli_dir = path.dirname(_module_dir)
    sys.path.append(_cli_dir)

import hcs_core.ctxp as ctxp
from hcs_core.ctxp.util import panic, CtxpException
import hcs_core.ctxp.cli_options as cli_options

# -----------------------------------------------------------
import hcs_core.ctxp.logger as logger

logger.setup()
logging.getLogger("charset_normalizer").setLevel(logging.WARN)
logging.getLogger("csp").setLevel(logging.INFO)
logging.getLogger("context").setLevel(logging.WARN)
logging.getLogger("init").setLevel(logging.WARN)
logging.getLogger("profile").setLevel(logging.WARN)
logging.getLogger("httpx").setLevel(logging.WARN)
# -----------------------------------------------------------


@click.group()
@click.version_option(package_name="hcs-cli")
@cli_options.verbose
@cli_options.output
@cli_options.field
@cli_options.id_only
@cli_options.first
@click.option("--profile", "-p", type=str, required=False, help="Specify the profile to use. Optional.")
@click.option("--upgrade-check/--no-upgrade-check", default=True, help="Check new version of HCS CLI.")
@click.option("--telemetry/--no-telemetry", default=True, help="Send telemetry")
def cli(**kwargs):
    upgrade_check = kwargs.get("upgrade_check")
    if upgrade_check:
        from hcs_core.util.versions import check_upgrade

        check_upgrade()

    profile = kwargs.get("profile")
    if profile:
        ctxp.profile._active_profile_name = profile


def _need_stack_trace(e) -> bool:
    program_errors = [
        LookupError,
        TypeError,
        ValueError,
        ArithmeticError,
        NameError,
        SyntaxError,
        KeyError,
    ]
    for t in program_errors:
        if isinstance(e, t):
            return True
    return False


def main():
    try:
        commands_dir = path.join(_module_dir, "cmds")
        config_path = path.join(_module_dir, "config")
        ctxp.init(cli_name="hcs", main_cli=cli, commands_dir=commands_dir, config_path=config_path)
    except Exception as e:
        # critical errors, must print stack trace.
        if _need_stack_trace(e):
            raise e
        else:
            # Other errors, no stack.
            panic(e)


def _on_http_error(e):
    try:
        err = json.loads(e.response.text)
    except:
        err = {"message": str(e), "response": e.response.text, "resource": str(e.request.url)}
    text = json.dumps(err, indent=4)
    panic(text)


if __name__ == "__main__":
    main()
