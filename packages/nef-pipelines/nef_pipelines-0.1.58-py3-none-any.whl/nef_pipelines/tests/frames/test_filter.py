import typer
from pynmrstar import Entry

from nef_pipelines.lib.test_lib import path_in_test_data, run_and_report
from nef_pipelines.tools.frames.rename import rename


app = typer.Typer()
app.command()(filter)

def test_filter_unassigned():
    ...
