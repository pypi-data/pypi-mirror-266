from dataclasses import dataclass, field
from dbt.cli.flags import Flags
from typing import Any, Set
from dbt.config.runtime import RuntimeConfig
from dbt.contracts.graph.manifest import Manifest
from dbt.adapters.base import BaseRelation


@dataclass
class IUnitTestContext:
    schema_suffix: str
    source_schema: str
    flags: Flags
    config: RuntimeConfig
    manifest: Manifest
    required_schemas: Set[BaseRelation] = field(default_factory=lambda: set())
