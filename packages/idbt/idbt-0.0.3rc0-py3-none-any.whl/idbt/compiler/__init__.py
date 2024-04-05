from typing import Optional
from dbt.compilation import Compiler
from dbt.contracts.graph.nodes import ManifestSQLNode, Dict, Any
from dbt.contracts.graph.manifest import Manifest
from dbt.config import RuntimeConfig
from dbt.contracts.graph.nodes import (
    ManifestNode,
)
from dbt.context.providers import ModelContext, RuntimeProvider


def generate_runtime_unit_test_context(
    model: ManifestNode,
    config: RuntimeConfig,
    manifest: Manifest,
) -> Dict[str, Any]:

    ctx = ModelContext(model, config, manifest, RuntimeProvider(), None)
    return ctx.to_dict()


class IUnittestCompiler(Compiler):
    def __init__(self, config) -> None:
        super().__init__(config)

    def _compile_code(
        self,
        node: ManifestSQLNode,
        manifest: Manifest,
        extra_context: Optional[Dict[str, Any]] = None,
    ) -> ManifestSQLNode:
        node = super()._compile_code(node, manifest, extra_context)
        return node

    # def _create_node_context(
    #     self,
    #     node: ManifestSQLNode,
    #     manifest: Manifest,
    #     extra_context: Dict[str, Any],
    # ) -> Dict[str, Any]:
    #     return generate_runtime_unit_test_context(node, self.config, manifest)
