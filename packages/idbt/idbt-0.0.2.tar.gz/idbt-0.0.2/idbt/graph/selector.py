from typing import Set, Optional
from dbt.node_types import NodeType
from dbt.graph import Graph, UniqueId
from dbt.graph.selector import NodeSelector, SelectionSpec
from dbt.contracts.graph.manifest import Manifest
from dbt.contracts.state import PreviousState


def get_package_names(nodes):
    return set([node.split(".")[1] for node in nodes])


def can_select_indirectly(node):
    """If a node is not selected itself, but its parent(s) are, it may qualify
    for indirect selection.
    Today, only Test nodes can be indirectly selected. In the future,
    other node types or invocation flags might qualify.
    """
    if node.resource_type == NodeType.Test:
        return True
    else:
        return False


class UIDSelector(NodeSelector):
    def __init__(
        self,
        graph: Graph,
        manifest: Manifest,
        previous_state: Optional[PreviousState],
        selected_uid: Set[UniqueId],
        include_empty_nodes: bool = False,
    ) -> None:
        self.selected_uid = selected_uid
        super().__init__(
            graph=graph,
            manifest=manifest,
            previous_state=previous_state,
            include_empty_nodes=include_empty_nodes,
        )

    def get_selected(self, spec: SelectionSpec) -> Set[UniqueId]:
        return self.selected_uid
