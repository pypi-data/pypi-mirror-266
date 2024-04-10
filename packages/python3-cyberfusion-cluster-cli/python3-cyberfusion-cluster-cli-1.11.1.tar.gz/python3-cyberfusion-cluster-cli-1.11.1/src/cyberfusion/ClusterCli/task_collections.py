"""Crons subcommands."""

import typer

from cyberfusion.ClusterCli._utilities import (
    catch_api_exception,
    get_support,
    wait_for_task,
)
from cyberfusion.ClusterSupport.task_collections import TaskCollection

app = typer.Typer()


@app.command()
@catch_api_exception
def results(
    uuid: str,
) -> None:
    """Get task collection results."""
    wait_for_task(
        task_collection_uuid=uuid,
    )


@app.command()
@catch_api_exception
def retry(uuid: str) -> None:
    """Retry task collection."""
    TaskCollection.retry(get_support(), uuid)

    wait_for_task(task_collection_uuid=uuid)
