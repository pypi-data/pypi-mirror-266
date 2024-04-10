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

from hcs_core.sglib.client_util import hdc_service_client, default_crud, wait_for_res_status
from hcs_core.util.query_util import PageRequest

_client = hdc_service_client("images")
_crud = default_crud(_client, "/v1/vsphere/gold-patterns", "gold-patterns")


def get(id: str, org_id: str, **kwargs):
    ret = _crud.get(id, org_id, **kwargs)
    return _formalize_gold_pattern_model(ret)


def list(org_id: str, **kwargs):
    ret = _crud.list(org_id, **kwargs)
    ret2 = []
    for r in ret:
        ret2.append(_formalize_gold_pattern_model(r))
    return ret2


def create(payload: dict, **kwargs):
    ret = _crud.create(payload, **kwargs)
    return _formalize_gold_pattern_model(ret)


delete = _crud.delete


def _formalize_gold_pattern_model(data):
    if data:
        return data["goldPattern"]
    return data
