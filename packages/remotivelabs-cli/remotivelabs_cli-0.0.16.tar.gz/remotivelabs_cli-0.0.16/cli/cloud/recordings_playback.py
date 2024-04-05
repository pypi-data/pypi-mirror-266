from __future__ import annotations

import datetime
import json
import tempfile
from typing import List

import grpc
import rich
import typer
from rich.progress import Progress, SpinnerColumn, TextColumn

from cli.errors import ErrorPrinter

from ..broker.lib.broker import Broker
from . import rest_helper as rest

app = typer.Typer(
    help="""
Support for playback of a recording on a cloud broker, make sure to always mount a recording first
"""
)


@app.command()
def play(
    recording_session: str = typer.Argument(..., help="Recording session id", envvar="REMOTIVE_CLOUD_RECORDING_SESSION"),
    broker: str = typer.Option(None, help="Broker to use"),
    project: str = typer.Option(..., help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT"),
    show_progress: bool = typer.Option(False, help="Show progress after started playing"),
    repeat: bool = typer.Option(False, help="Repeat recording - must keep command running in terminal"),
):
    """
    Start playing a recording.
    There is no problem invoking play multiple times since if it is already playing the command will be ignored.
    Use --repeat to have the recording replayed when it reaches the end.
    """

    _do_change_playback_mode("play", recording_session, broker, project, progress_on_play=show_progress, repeat=repeat)


@app.command()
def pause(
    recording_session: str = typer.Argument(..., help="Recording session id", envvar="REMOTIVE_CLOUD_RECORDING_SESSION"),
    broker: str = typer.Option(None, help="Broker to use"),
    project: str = typer.Option(..., help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT"),
):
    """
    Pause a recording
    """
    _do_change_playback_mode("pause", recording_session, broker, project)


@app.command()
def progress(
    recording_session: str = typer.Argument(..., help="Recording session id", envvar="REMOTIVE_CLOUD_RECORDING_SESSION"),
    broker: str = typer.Option(None, help="Broker to use"),
    project: str = typer.Option(..., help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT"),
):
    """
    Shows progress of the recording playing.
    Use --repeat to have the recording replayed when it reaches the end.
    """
    _do_change_playback_mode("status", recording_session, broker, project)


@app.command()
def seek(
    recording_session: str = typer.Argument(..., help="Recording session id", envvar="REMOTIVE_CLOUD_RECORDING_SESSION"),
    seconds: int = typer.Option(..., min=0, help="Target offset in seconds"),
    broker: str = typer.Option(None, help="Broker to use"),
    project: str = typer.Option(..., help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT"),
):
    """
    Seek seconds into a recording
    """
    _do_change_playback_mode("seek", recording_session, broker, project, seconds)


@app.command()
def stop(
    recording_session: str = typer.Argument(..., help="Recording session id", envvar="REMOTIVE_CLOUD_RECORDING_SESSION"),
    broker: str = typer.Option(None, help="Broker to use"),
    project: str = typer.Option(..., help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT"),
):
    """
    Stop playing
    """
    _do_change_playback_mode("stop", recording_session, broker, project)


def _do_change_playback_mode(
    mode: str,
    recording_session: str,
    broker: str,
    project: str,
    seconds: int | None = None,
    progress_on_play: bool = False,
    repeat: bool = False,
):  # noqa: C901
    response = rest.handle_get(f"/api/project/{project}/files/recording/{recording_session}", return_response=True)
    r = json.loads(response.text)
    recordings: list = r["recordings"]
    files = list(map(lambda rec: {"recording": rec["fileName"], "namespace": rec["metadata"]["namespace"]}, recordings))

    if broker is not None:
        response = rest.handle_get(f"/api/project/{project}/brokers/{broker}", return_response=True, allow_status_codes=[404])
    else:
        response = rest.handle_get(f"/api/project/{project}/brokers/personal", return_response=True, allow_status_codes=[404])
    if response.status_code == 404:
        broker_arg = ""
        if broker is not None:
            broker_arg = f" --broker {broker} --ensure-broker-started"
        ErrorPrinter.print_generic_error("You need to mount the recording before you play")
        ErrorPrinter.print_hint(f"remotive cloud recordings mount {recording_session}{broker_arg} --project {project}")
        exit(1)

    broker_info = json.loads(response.text)
    broker = Broker(broker_info["url"], None)

    _verify_recording_on_broker(broker, recording_session, mode, project)

    if mode == "pause":
        broker.pause_play(files, True)
    elif mode == "play":
        broker.play(files, True)
        if progress_on_play or repeat:
            _track_progress(broker, repeat, files)
    elif mode == "seek":
        broker.seek(files, int(seconds * 1000000), True)
    elif mode == "stop":
        broker.seek(files, 0, True)
    elif mode == "status":
        _track_progress(broker, repeat, files)
    else:
        raise Exception(f"Illegal command {mode}")


def _track_progress(broker: Broker, repeat: bool, files: List):
    p = Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True)
    t = p.add_task("label", total=1)
    if repeat:
        rich.print(":point_right: Keep this command running in terminal to keep the recording play with repeat")
    with p:

        def print_progress(offset: int, total: int, current_mode: str):
            p.update(
                t,
                description=f"{(datetime.timedelta(seconds=offset))} " f"/ {(datetime.timedelta(seconds=total))} ({current_mode})",
            )

        broker.listen_on_playback(repeat, files, print_progress)


def _verify_recording_on_broker(broker: Broker, recording_session: str, mode: str, project: str):
    try:
        # Here we try to verify that we are operating on a recording that is mounted on the
        # broker so we can verify this before we try playback and can also present some good
        # error messages
        tmp = tempfile.NamedTemporaryFile()
        broker.download(".cloud.context", tmp.name, True)
        with open(tmp.name, "r") as f:
            json_context = json.loads(f.read())
            if json_context["recordingSessionId"] != recording_session:
                ErrorPrinter.print_generic_error(
                    f"The recording id mounted is '{json_context['recordingSessionId']}' "
                    f"which  not the same as you are trying to {mode}, "
                    "use cmd below to mount this recording"
                )
                ErrorPrinter.print_hint(f"remotive cloud recordings mount {recording_session} --project {project}")
                exit(1)
    except grpc.RpcError as rpc_error:
        if rpc_error.code() == grpc.StatusCode.NOT_FOUND:
            ErrorPrinter.print_generic_error(f"You must use mount to prepare a recording before you can use {mode}")
            ErrorPrinter.print_hint(f"remotive cloud recordings mount {recording_session} --project {project}")
        else:
            ErrorPrinter.print_grpc_error(rpc_error)
        exit(1)
