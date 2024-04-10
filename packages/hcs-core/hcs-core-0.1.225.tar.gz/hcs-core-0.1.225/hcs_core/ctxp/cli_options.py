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


verbose = click.option(
    "--verbose",
    "-v",
    count=True,
    default=0,
    help="Print debug logs",
)

output = click.option(
    "--output",
    "-o",
    type=click.Choice(["json", "json-compact", "yaml", "text"]),
    default="json",
    help="Specify output format",
)

field = click.option(
    "--field",
    "-f",
    type=str,
    required=False,
    help="Specify fields to output",
)

wait = click.option(
    "--wait",
    "-w",
    type=str,
    required=False,
    default="0",
    help="Wait time. E.g. '30s', or '5m'. Default: 10m. Specify '0' to disable waiting and return immediately.",
)
search = click.option(
    "--search",
    "-s",
    type=str,
    required=False,
    help="Specify REST search. E.g. 'name $eq something'. Note: use single quote in bash/sh.",
)
sort = click.option(
    "--sort",
    type=str,
    required=False,
    help="Ascending/Descending. Format is property,{asc|desc} and default is ascending",
)
limit = click.option(
    "--limit", "-l", type=int, required=False, default=20, help="Optionally, specify the number of records to fetch."
)
id_only = click.option(
    "--id-only/--full-object", "-i", type=bool, required=False, default=False, help="Return only id of the document"
)
first = click.option(
    "--first/--all",
    type=bool,
    required=False,
    default=False,
    help="Return only the first object, if the result is a list.",
)

force = click.option("--force/--grace", type=bool, default=True, help="Specify deletion mode: forceful, or graceful.")

confirm = click.option(
    "--confirm/--dry-run", "-y", type=bool, default=False, help="Confirm the operation without prompt."
)
