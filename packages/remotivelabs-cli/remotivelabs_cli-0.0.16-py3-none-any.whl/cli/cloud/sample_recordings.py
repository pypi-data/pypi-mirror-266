import json

import typer

from . import rest_helper as rest

app = typer.Typer()


@app.command(name="import", help="Import sample recording into project")
def do_import(
    recording_session: str = typer.Argument(..., help="Recording session id"),
    project: str = typer.Option(..., help="Project to import sample recording into", envvar="REMOTIVE_CLOUD_PROJECT"),
):
    rest.handle_post(url=f"/api/samples/files/recording/{recording_session}/copy", body=json.dumps({"projectUid": project}))


@app.command("list")
def list():
    """
    List available sample recordings
    """

    rest.handle_get("/api/samples/files/recording")
