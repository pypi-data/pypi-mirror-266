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

from .jsondot import dotdict
from .profile_store import profile_store, fstore


def _store() -> fstore:
    return profile_store("context")


def list() -> list[str]:
    return _store().keys()


def get(name: str, reload: bool = False, default=None) -> dotdict:
    return _store().get(key=name, reload=reload, default=default)


def set(name: str, data: dict):
    return _store().save(name, data)


def delete(name: str):
    return _store().delete(name)


def file(name: str):
    return _store()._get_path(name)


def clear():
    return _store().clear()
