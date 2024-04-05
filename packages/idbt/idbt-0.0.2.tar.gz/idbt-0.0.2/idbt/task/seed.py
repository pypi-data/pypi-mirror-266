from dbt.task.seed import SeedTask, SeedRunner
from dbt.exceptions import (
    DbtInternalError,
)
from dbt.contracts.graph.manifest import Manifest
from dbt.graph.queue import GraphQueue
from idbt.context.i_unit_test import IUnitTestContext
from idbt.graph.selector import UIDSelector
from dbt.graph.selector import NodeSelector
from dbt.graph import UniqueId
from dbt.contracts.results import NodeStatus
from typing import AbstractSet, Set
import copy


class IUnitTestSeedRunner(SeedRunner):
    def __init__(self, config, adapter, node, node_index, num_nodes) -> None:
        super().__init__(config, adapter, node, node_index, num_nodes)

    def print_result_line(self, result):
        """
        This hook is to skip model success print
        """
        if result.status == NodeStatus.Success:
            return
        super().print_result_line(result)


"""
This seed task is implemented for selecting specific node's uuid via constructor instead of using NodeSelector
"""


class IUnitTestSeedTask(SeedTask):
    def __init__(
        self,
        args,
        config,
        manifest: Manifest,
        selected_seednodes: Set[UniqueId],
        i_unit_test_context: IUnitTestContext,
    ) -> None:
        self.selected_seednodes = selected_seednodes
        self.i_unit_test_context = i_unit_test_context
        super().__init__(args, config, manifest)

    def get_runner_type(self, _):
        return IUnitTestSeedRunner

    def get_node_selector(self) -> NodeSelector:
        return UIDSelector(
            graph=self.graph,
            manifest=self.manifest,
            previous_state=self.previous_state,
            selected_uid=self.selected_seednodes,
        )

    def before_run(self, adapter, selected_uids: AbstractSet[str]) -> None:
        """
        This hook is to get the required_schemas and assign it into IUnitTestContext
        """
        required_schemas = self.get_model_schemas(adapter, selected_uids)
        for required_schema in required_schemas:
            self.i_unit_test_context.required_schemas.add(required_schema)
        super().before_run(adapter, selected_uids)

    def task_end_messages(self, results) -> None:
        """
        This hook is to skip printing seedtask "Completed successfully"
        """
        pass
