import copy
from dbt.task.run import ModelRunner
from dbt.contracts.graph.manifest import Manifest
from dbt.parser import manifest
from functools import partialmethod
from dbt.contracts.graph.nodes import ModelNode
from dbt.task.runnable import GraphRunnableTask
from dbt.contracts.graph.nodes import  ManifestNode
   
copied_runtime_initialize = copy.deepcopy(GraphRunnableTask._runtime_initialize)
copied_compile_and_execute =copy.deepcopy(ModelRunner.compile_and_execute)
copied_parse_manifest = copy.deepcopy(manifest.parse_manifest)
copied_execute = copy.deepcopy(ModelRunner.execute)

def _wrapper_runtime_initialize(self,uuid:str):
    """
    this is a wrapper to access the manifest without compiled
    """
    copied_runtime_initialize(self)
    manifest:Manifest = self.manifest
    for attr, value in manifest.nodes.items():
        if(isinstance(value,ModelNode)):
            value.schema = f'{value.schema}_unittest_{uuid}'
          

def _wrapper_compile_and_execute(self, manifest:Manifest, ctx,uuid:str):
    """
    this is a wrapper to access the adapter and do some stuffs before execute each note
    """
    return copied_compile_and_execute(self, manifest, ctx)

def _wrapper_execute(self, model:ManifestNode, manifest:Manifest):
    """
    this is a wrapper to access to process of executing each node
    """
    print('_wrapper_execute')
    
    return copied_execute(self,model,manifest)

def _wrapper_parse_manifest(*args, **kwargs):
    manifest = copied_parse_manifest(*args, **kwargs)
    return manifest

def register(uuid:str):
    """
    Unit test will be run like dbt run flow but change the schema by a uuid prefix.
    This function receive the  schema and register hooks
    Args:
        uuid: uuid string to create schema prefix ex: 5a9ef4bc-3d08-474b-9b02-82faeb146c88
    """
    print('create hook ModelRunner.compile_and_execute')
    # GraphRunnableTask._runtime_initialize = partialmethod(_wrapper_runtime_initialize,uuid=uuid)
    # ModelRunner.compile_and_execute = partialmethod(_wrapper_compile_and_execute,uuid=uuid)
    # ModelRunner.execute = _wrapper_execute
    # manifest.parse_manifest = _wrapper_parse_manifest




    



