from dataclasses import dataclass
from datetime import datetime
import time
from typing import AbstractSet, List, Optional
from dbt.task.run import RunTask, ModelRunner, fire_event
from dbt.contracts.graph.manifest import Manifest
from dbt.graph import UniqueId
from dbt.contracts.graph.nodes import ModelNode, SeedNode
from idbt.context.i_unit_test import IUnitTestContext
from dbt.config.runtime import RuntimeConfig
from typing import Set, Dict, Union
from idbt.loader import FileLoader
from idbt.manifest import IdbtManifest
from idbt.manifest.i_unit_test import IUnitTestDefinition
from idbt.task.seed import IUnitTestSeedTask
import copy
from dbt.exceptions import (
    DbtRuntimeError,
)
from dbt.contracts.results import NodeStatus, RunResult
from dbt.events.types import (
    LogStartLine,
)
from dbt.events.base_types import EventLevel
from idbt.events.types import LogModelResult as LogIUnitTestResult
from dbt.contracts.results import RunStatus
from dbt.adapters.factory import get_adapter

PARAMETER_PREFIX = "unittest_param"


@dataclass
class TestInputFilesMapper:
    key: str
    file: str
    seednode: SeedNode


class IUnitTestRunner(ModelRunner):
    i_unit_test_context: IUnitTestContext
    idbt_manifest: IdbtManifest
    seednodes: List[SeedNode]

    def __init__(self, config, adapter, node, node_index, num_nodes) -> None:
        super().__init__(config, adapter, node, node_index, num_nodes)

    def compile_and_execute(self, manifest: Manifest, ctx):
        """
        This hook is to load the IDBT manifest before execute each model
        """
        runtime_config: RuntimeConfig = self.config
        self.idbt_manifest = FileLoader().load(runtime_config.model_paths)
        self.seednodes = []
        for key in manifest.nodes:
            node = manifest.nodes[key]
            if isinstance(node, SeedNode):
                self.seednodes.append(node)
        result = super().compile_and_execute(manifest, ctx)
        return result

    def execute(self, model: ModelNode, manifest: Manifest):
        result: RunResult = None
        is_fail_test = False
        if model.identifier in self.idbt_manifest.i_unit_test:
            unit_test_definitions = self.idbt_manifest.i_unit_test[model.identifier]

            for test_index, unit_test_definition in enumerate(unit_test_definitions):
                compiled_model_result, assert_result = self._execute_unit_test(
                    unit_test_definition,
                    manifest,
                    model,
                    test_index,
                    unit_test_definitions.__len__(),
                )
                result = compiled_model_result
                is_fail_test = True if assert_result == False else is_fail_test

        if result == None:
            return RunResult(
                status=RunStatus.Success,
                thread_id="thread_id",
                execution_time=0,
                timing=[],
                message="NOT_FOUND_UNIT_TEST",
                node=model,
                adapter_response={},
                failures=None,
            )
        result.status = NodeStatus.Error if is_fail_test else result.status
        return result

    def print_result_line(self, result: RunResult):
        """
        This hook is to skip model success print and print a warn message for models don't have unittest
        """
        if result.message == "NOT_FOUND_UNIT_TEST":
            fire_event(
                LogIUnitTestResult(
                    description=f"""Not found any unittest for model: {self.node.identifier}""",
                    status=result.status,
                    index=0,
                    total=0,
                    execution_time=result.execution_time,
                    node_info=self.node.node_info,
                ),
                level=EventLevel.INFO,
            )
        if result.status == NodeStatus.Success:
            return
        super().print_result_line(result)

    def describe_node(self):
        """This hook is to change describe of loging"""
        return f"""All unittests for model: {self.node.identifier}"""

    def after_execute(self, result):
        """This hook is to skip handle NodeResult return in execute function if it's None"""
        if result != None:
            super().after_execute(result)

    def _execute_unit_test(
        self,
        unit_test_definition: IUnitTestDefinition,
        manifest: Manifest,
        model: ModelNode,
        test_index: int,
        total_test_case: int,
    ) -> RunResult:
        self._print_unit_test_start_line(unit_test_definition, test_index, total_test_case)
        seednodes, seednode_ids, test_input_file_mappers, expected_output_seednode = (
            self._get_required_seednodes(unit_test_definition)
        )
        self._execute_required_seednodes_tasks(unit_test_definition, seednode_ids, manifest)
        raw_code, additional_context = self._build_jinja_raw_code_and_parameter(
            model, test_input_file_mappers
        )
        recompiled_model = self._recompile_model(model, raw_code, manifest, additional_context)

        with self.adapter.connection_named(
            f"unit_test_{unit_test_definition.model}_{unit_test_definition.name}"
        ):
            compiled_model_result = super().execute(recompiled_model, manifest)

            # DO NOT execute the assert macro if the compiled model run fail#
            if compiled_model_result.status == NodeStatus.Error:
                return compiled_model_result, False

            assert_result = self._execute_assert_macro(
                unit_test_definition, manifest, recompiled_model, expected_output_seednode
            )
            if assert_result == False:
                compiled_model_result.status = NodeStatus.Error
            self._print_unit_test_result_line(
                compiled_model_result, unit_test_definition, test_index, total_test_case
            )
            return compiled_model_result, assert_result

    def _print_unit_test_result_line(
        self,
        result,
        unit_test_definition: IUnitTestDefinition,
        test_index: int,
        total_test_case: int,
    ):
        if result.status == NodeStatus.Error:
            status = result.status
            level = EventLevel.ERROR
        else:
            status = result.message
            level = EventLevel.INFO
        fire_event(
            LogIUnitTestResult(
                description=self._get_unit_test_description(unit_test_definition),
                status=status,
                index=test_index,
                total=total_test_case,
                execution_time=result.execution_time,
                node_info=self.node.node_info,
            ),
            level=level,
        )

    def _get_unit_test_description(self, unit_test_definition: IUnitTestDefinition):
        return f"""Unittest name: {unit_test_definition.name} of model: {self.node.identifier}"""

    def _print_unit_test_start_line(
        self,
        unit_test_definition: IUnitTestDefinition,
        test_index: int,
        total_test_case: int,
    ):
        fire_event(
            LogStartLine(
                description=self._get_unit_test_description(unit_test_definition),
                index=test_index,
                total=total_test_case,
                node_info=self.node.node_info,
            )
        )

    def _execute_assert_macro(
        self,
        unit_test_definition: IUnitTestDefinition,
        manifest: Manifest,
        model: ModelNode,
        expected_output_seednode: SeedNode,
    ) -> bool:
        assert_macro_context = {}
        for param in unit_test_definition.assert_macro.parameters:
            assert_macro_context[param.key] = param.value
        assert_macro_context["model"] = self._get_node_path(model)
        assert_macro_context["expected_output"] = self._get_node_path(expected_output_seednode)

        result = self.adapter.execute_macro(
            unit_test_definition.assert_macro.name,
            kwargs={"assert_macro_context": assert_macro_context},
            manifest=manifest,
        )
        return result

    def _get_node_path(self, node: Union[SeedNode, ModelNode]) -> str:
        relation = self.adapter.Relation.create(
            database=node.database,
            schema=node.schema,
            identifier=node.identifier,
        )
        return str(relation)

    def _recompile_model(
        self,
        old_model: ModelNode,
        raw_code: str,
        manifest: Manifest,
        additional_context: Dict[str, str],
    ) -> ModelNode:
        copied_model = copy.deepcopy(old_model)
        copied_model.raw_code = raw_code
        compiler = self.adapter.get_compiler()
        return compiler.compile_node(copied_model, manifest, additional_context)

    def _build_jinja_raw_code_and_parameter(
        self, model: ModelNode, test_input_file_mappers: List[TestInputFilesMapper]
    ) -> tuple[str, Dict[str, str]]:
        """
        Rebuild the raw_code and additional paramater for re-compiling model node
        Have to use adapter relation to ensure the relation path is suite with dialect convention
        """

        raw_code = model.raw_code
        parameter: Dict[str, str] = {}
        parameter_index = 0

        for test_input_file_mapper in test_input_file_mappers:
            key = f"{PARAMETER_PREFIX}_{parameter_index}"
            raw_code = raw_code.replace(test_input_file_mapper.key, key)
            parameter[key] = self._get_node_path(test_input_file_mapper.seednode)
            parameter_index += 1

        return raw_code, parameter

    def _execute_required_seednodes_tasks(
        self,
        unit_test_definition: IUnitTestDefinition,
        seednode_ids: Set[UniqueId],
        manifest: Manifest,
    ):
        """
        Execute the SeedTask with overiding flags
        Used editted manifest to ensure that the seednodes' schema is changed
        """

        flags = copy.deepcopy(self.i_unit_test_context.flags)
        object.__setattr__(flags, "show", False)
        # EVENT_MANAGER is inialized globally, so reset flag log level won't work
        # flags.__setattr__("QUIET", True)
        # flags.__setattr__("quiet", True)
        # flags.__setattr__("log_level", "error")
        # flags.__setattr__("LOG_LEVEL", "error")
        task = IUnitTestSeedTask(
            flags,
            self.i_unit_test_context.config,
            manifest,
            selected_seednodes=seednode_ids,
            i_unit_test_context=self.i_unit_test_context,
        )
        results = task.run()
        success = task.interpret_results(results)
        if success == False:
            raise DbtRuntimeError(
                f"""Fail uploading seed for unittest.
                Please recheck given input and expected output file for unittest:
                    - model: {unit_test_definition.model}
                    - name:  {unit_test_definition.name}"""
            )

    def _get_required_seednodes(
        self, unit_test_definition: IUnitTestDefinition
    ) -> tuple[List[SeedNode], Set[UniqueId], List[TestInputFilesMapper], SeedNode]:
        """
        Based on test definition, loop all seednodes in manifest to find the correspondence
        Also include the output file seednode
        """

        seednodes: List[SeedNode] = []
        test_input_file_mappers: List[TestInputFilesMapper] = []
        expected_output_seednode: Optional[SeedNode] = None

        for given in unit_test_definition.given:
            file = given.file
            corresponded_seednode = None
            for seednode in self.seednodes:
                if seednode.original_file_path == file:
                    corresponded_seednode = seednode
                    test_input_file_mappers.append(
                        TestInputFilesMapper(
                            key=given.input, file=file, seednode=corresponded_seednode
                        )
                    )
                    seednodes.append(corresponded_seednode)
                    break
            if corresponded_seednode == None:
                raise Exception(f"Not found seednode for file: {file}")

        for seednode in self.seednodes:
            if seednode.original_file_path == unit_test_definition.expected_output_file:
                seednodes.append(seednode)
                expected_output_seednode = seednode
                break

        return (
            seednodes,
            set([node.unique_id for node in seednodes]),
            test_input_file_mappers,
            expected_output_seednode,
        )


class IUnitTestTask(RunTask):
    def __init__(self, args, config, manifest, i_unit_test_context: IUnitTestContext) -> None:
        self.i_unit_test_context = i_unit_test_context
        super().__init__(args, config, manifest)

    def _runtime_initialize(self):
        """
        This hook is to change model bide schema and seed node schema to let the flow create those schema
        """
        super()._runtime_initialize()
        manifest: Manifest = self.manifest
        for attr, value in manifest.nodes.items():
            if isinstance(value, ModelNode):
                value.schema = f"{value.schema}_unittest_{self.i_unit_test_context.schema_suffix}"
            if isinstance(value, SeedNode):
                value.schema = f"seed_data_unittest_{self.i_unit_test_context.schema_suffix}"

    def get_runner_type(self, _):
        return IUnitTestRunner

    def get_runner(self, node) -> IUnitTestRunner:
        runner: IUnitTestRunner = super().get_runner(node)
        runner.i_unit_test_context = self.i_unit_test_context
        return runner

    def before_run(self, adapter, selected_uids: AbstractSet[str]) -> None:
        """
        This hook is to get the required_schemas and assign it into IUnitTestContext
        """
        required_schemas = self.get_model_schemas(adapter, selected_uids)
        for required_schema in required_schemas:
            self.i_unit_test_context.required_schemas.add(required_schema)
        super().before_run(adapter, selected_uids)

    def _delete_unusage_schemas(self, adapter):
        with adapter.connection_named(f"unit_test_delete_unused_schemas"):
            for relation in self.i_unit_test_context.required_schemas:
                adapter.drop_schema(relation)

    def execute_with_hooks(self, selected_uids: AbstractSet[str]):
        """
        This hook is to delete unusage schema in finally block of code
        """
        adapter = get_adapter(self.config)
        self.started_at = time.time()
        try:
            self.before_run(adapter, selected_uids)
            res = self.execute_nodes()
            self.after_run(adapter, res)
        finally:
            self._delete_unusage_schemas(adapter)
            adapter.cleanup_connections()
            elapsed = time.time() - self.started_at
            self.print_results_line(self.node_results, elapsed)
            result = self.get_result(
                results=self.node_results, elapsed_time=elapsed, generated_at=datetime.utcnow()
            )

        return result
