import uuid
from dbt.task.run import RunTask
import click
from dbt.cli import requires, params as p
from dbt.cli.main import global_flags, cli
from dbt.cli.main import dbtRunner, dbtRunnerResult
from idbt.task.i_unit_test import IUnitTestTask
from idbt.context.i_unit_test import IUnitTestContext
import copy


@cli.command("unittest")
@click.pass_context
@global_flags
@p.defer
@p.deprecated_defer
@p.favor_state
@p.deprecated_favor_state
@p.exclude
@p.full_refresh
@p.profile
@p.profiles_dir
@p.project_dir
@p.select
@p.selector
@p.state
@p.defer_state
@p.deprecated_state
@p.target
@p.target_path
@p.threads
@p.vars
@requires.postflight
@requires.preflight
@requires.profile
@requires.project
@requires.runtime_config
@requires.manifest
def unittest(ctx, **kwargs):
    """Inter-k dbt unittest"""

    uuid_str = str(uuid.uuid4())
    source_schema = f"source_unittest_{uuid_str}"
    i_unit_test_context = IUnitTestContext(
        uuid_str,
        source_schema,
        flags=copy.deepcopy(ctx.obj["flags"]),
        config=copy.deepcopy(ctx.obj["runtime_config"]),
        manifest=copy.deepcopy(ctx.obj["manifest"]),
    )

    task = IUnitTestTask(
        ctx.obj["flags"], ctx.obj["runtime_config"], ctx.obj["manifest"], i_unit_test_context
    )

    results = task.run()
    success = task.interpret_results(results)
    return results, success


if __name__ == "__main__":
    cli()
