from __future__ import annotations

import glob
import json
import os
import re
import sys
import tempfile
from pathlib import Path

import grpc
import requests
import typer
from rich.progress import Progress, SpinnerColumn, TextColumn, track

from cli.errors import ErrorPrinter

from ..broker.lib.broker import Broker
from . import rest_helper as rest
from .recordings_playback import app as playback_app

app = typer.Typer()
app.add_typer(playback_app, name="playback")


def uid(p):
    print(p)
    return p["uid"]


# to be used in options
# autocompletion=project_names)
def project_names():
    r = requests.get(f"{rest.base_url}/api/bu/{rest.org}/project", headers=rest.headers)
    # sys.stderr.write(r.text)
    if r.status_code == 200:
        projects = r.json()
        names = map(lambda p: p["uid"], projects)
        return list(names)
    sys.stderr.write(f"Could not list projects due to {r.status_code}\n")
    raise typer.Exit(0)


@app.command("list")
def list_recordings(
    is_processing: bool = typer.Option(default=False, help="Use this option to see only those that are beeing processed or are invalid"),
    project: str = typer.Option(..., help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT"),
):
    """
    List all recording sessions in a project. You can choose to see all valid recordings (default) or use
    --is-processing and you will get those that are currently beeing processed or that failed to be validated.

    """

    if is_processing:
        rest.handle_get(f"/api/project/{project}/files/recording/processing")
    else:
        rest.handle_get(f"/api/project/{project}/files/recording")


@app.command(help="Shows details about a specific recording in project")
def describe(
    recording_session: str = typer.Argument(..., help="Recording session id", envvar="REMOTIVE_CLOUD_RECORDING_SESSION"),
    project: str = typer.Option(..., help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT"),
):
    rest.handle_get(f"/api/project/{project}/files/recording/{recording_session}")


# @app.command(help="Shows details about a specific recording in project")
# def copy(recording_session: str = typer.Argument(..., help="Recording session id"),
#         target_project: str = typer.Option(..., help="Which project to copy the recording to"),
#         project: str = typer.Option(..., help="Project ID", envvar='REMOTIVE_CLOUD_PROJECT')):
#    rest.handle_post(url=f"/api/project/{project}/files/recording/{recording_session}/copy",
#                     body=json.dumps({'projectUid': target_project}))


def do_start(name: str, project: str, api_key: str, return_response: bool = False):
    if api_key == "":
        body = {"size": "S"}
    else:
        body = {"size": "S", "apiKey": api_key}

    name = name if name is not None else "personal"
    return rest.handle_post(
        f"/api/project/{project}/brokers/{name}",
        body=json.dumps(body),
        return_response=return_response,
        progress_label=f"Starting {name}...",
    )


@app.command(help="Prepares all recording files and transformations to be available for playback")
def mount(
    recording_session: str = typer.Argument(..., help="Recording session id", envvar="REMOTIVE_CLOUD_RECORDING_SESSION"),
    broker: str = typer.Option(None, help="Broker to use"),
    ensure_broker_started: bool = typer.Option(default=False, help="Ensure broker exists, start otherwise"),
    transformation_name: str = typer.Option("default", help="Specify a custom signal transformation to use"),
    project: str = typer.Option(..., help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT"),
):
    rest.ensure_auth_token()

    rest.handle_get(f"/api/project/{project}/files/recording/{recording_session}", return_response=True)

    if broker is None:
        r = rest.handle_get(url=f"/api/project/{project}/brokers/personal", return_response=True, allow_status_codes=[404])

        if r.status_code == 200:
            broker = r.json()["shortName"]

        elif r.status_code == 404:
            r = do_start(None, project, "", return_response=True)
            if r.status_code != 200:
                print(r.text)
                exit(0)
            broker = r.json()["shortName"]
        else:
            sys.stderr.write(f"Got http status code {r.status_code}")
            typer.Exit(0)
    else:
        r = rest.handle_get(url=f"/api/project/{project}/brokers/{broker}", return_response=True, allow_status_codes=[404])

        if r.status_code == 404:
            if ensure_broker_started:
                r = do_start(broker, project, "", return_response=True)

                if r.status_code != 200:
                    print(r.text)
                    exit(1)
            else:
                ErrorPrinter.print_generic_error(f"Broker {broker} not running")
                exit(1)
        elif r.status_code != 200:
            sys.stderr.write(f"Got http status code {r.status_code}")
            typer.Exit(1)
    broker_config_query = ""
    if transformation_name != "default":
        broker_config_query = f"?brokerConfigName={transformation_name}"

    rest.handle_get(
        f"/api/project/{project}/files/recording/{recording_session}/upload{broker_config_query}",
        params={"brokerName": broker},
        return_response=True,
        progress_label="Preparing recording on broker...",
    )
    print("Successfully mounted recording on broker")


@app.command(help="Downloads the specified recording file to disk")
def download_recording_file(
    recording_file_name: str = typer.Argument(..., help="Recording file to download"),
    recording_session: str = typer.Option(
        ..., help="Recording session id that this file belongs to", envvar="REMOTIVE_CLOUD_RECORDING_SESSION"
    ),
    project: str = typer.Option(..., help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT"),
):
    rest.ensure_auth_token()
    get_signed_url_resp = requests.get(
        f"{rest.base_url}/api/project/{project}/files/recording/{recording_session}/recording-file/{recording_file_name}",
        headers=rest.headers,
        allow_redirects=True,
    )
    if get_signed_url_resp.status_code == 200:
        # Next download the actual file
        rest.download_file(recording_file_name, get_signed_url_resp.json()["downloadUrl"])
        print(f"Downloaded {recording_file_name}")


@app.command(name="delete")
def delete(
    recording_session: str = typer.Argument(..., help="Recording session id", envvar="REMOTIVE_CLOUD_RECORDING_SESSION"),
    project: str = typer.Option(..., help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT"),
):
    """
    Deletes the specified recording session including all media files and configurations.

    """
    rest.handle_delete(f"/api/project/{project}/files/recording/{recording_session}")


@app.command(name="delete-recording-file")
def delete_recording_file(
    recording_file_name: str = typer.Argument(..., help="Recording file to download"),
    recording_session: str = typer.Option(
        ..., help="Recording session id that this file belongs to", envvar="REMOTIVE_CLOUD_RECORDING_SESSION"
    ),
    project: str = typer.Option(..., help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT"),
):
    """
    Deletes the specified recording file

    """
    rest.handle_delete(f"/api/project/{project}/files/recording/{recording_session}/recording-file/{recording_file_name}")


@app.command()
def upload(
    path: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=False,
        writable=False,
        readable=True,
        resolve_path=True,
        help="Path to recording file to upload",
    ),
    project: str = typer.Option(..., help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT"),
    recording_type: str = typer.Option("remotive-broker", help="Type of recording"),
    signal_database: str = typer.Option(None, help="Signal database to use with candump"),
):
    # TODO - Test to do this with typer Enums instead
    # Validate this here to validate before we start any progress
    if recording_type == "candump" and (signal_database is None or signal_database == ""):
        ErrorPrinter.print_hint("Option --signal-database is required with --recording-type is 'candump'")
        exit(1)

    filename = os.path.basename(path.name)
    rest.ensure_auth_token()

    if recording_type == "candump":
        rest.headers["x-recording-type"] = "candump"
        r = rest.handle_post(
            url=f"/api/project/{project}/files/recording/{filename}",
            return_response=True,
            progress_label="Requesting recording upload...",
            body=json.dumps({"dbcFile": signal_database}),
        )
    else:
        r = rest.handle_post(f"/api/project/{project}/files/recording/{filename}", return_response=True)

    response = rest.upload_file_with_signed_url(
        path=path.name, url=r.text, upload_headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    if 200 <= response.status_code < 300:
        print(
            "File successfully uploaded, please run 'remotive cloud recordings list' "
            "to verify that the recording was successfully processed"
        )
    else:
        rest.err_console.print(f":boom: [bold red]Got status code[/bold red]: {response.status_code} {response.text}")


@app.command()
def upload_broker_configuration(
    directory: str = typer.Argument(..., help="Configuration directory"),
    recording_session: str = typer.Option(..., help="Recording session id", envvar="REMOTIVE_CLOUD_RECORDING_SESSION"),
    project: str = typer.Option(..., help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT"),
    overwrite: bool = typer.Option(False, help="Overwrite existing configuration if it exists"),
):
    # Must end with /
    if not directory.endswith("/"):
        directory = f"{directory}/"

    #
    # List files in specified directory. Look for interfaces.json and use that directory where this is located
    # as configuration home directory
    #
    files = list(filter(lambda item: "interfaces.json" in item, glob.iglob(directory + "**/**", recursive=True)))
    if len(files) == 0:
        sys.stderr.write("No interfaces.json found in directory, this file is required")
        raise typer.Exit(1)
    if len(files) > 1:
        sys.stderr.write(f"{len(files)} interfaces.json found in directoryw which is not supported")
        raise typer.Exit(1)
    broker_config_dir_name = os.path.dirname(files[0]).rsplit("/", 1)[-1]

    #
    # Get the current details about broker configurations to see if a config with this
    # name already exists
    #
    # task = progress.add_task(description=f"Preparing upload of {broker_config_dir_name}", total=1)
    details_resp = rest.handle_get(f"/api/project/{project}/files/recording/{recording_session}", return_response=True)
    details = details_resp.json()
    existing_configs = details["brokerConfigurations"]
    if len(existing_configs) > 0:
        data = list(filter(lambda x: x["name"] == broker_config_dir_name, existing_configs))
        if len(data) > 0:
            if overwrite:
                rest.handle_delete(
                    f"/api/project/{project}/files/recording/{recording_session}/configuration/{broker_config_dir_name}", quiet=True
                )
            else:
                sys.stderr.write("Broker configuration already exists, use --overwrite to replace\n")
                raise typer.Exit(1)

    #
    # From the list of files, create a tuple of local_path to the actual file
    # and a remote path as it should be stored in cloud
    #
    file_infos = list(
        map(
            lambda item: {"local_path": item, "remote_path": f"/{broker_config_dir_name}{item.rsplit(broker_config_dir_name, 1)[-1]}"},
            glob.iglob(directory + "**/*.*", recursive=True),
        )
    )

    #
    # convert this remote paths and ask cloud to prepare upload urls for those
    #
    json_request_upload_urls_req = {"name": "not_used", "paths": list(map(lambda x: x["remote_path"], file_infos))}

    response = rest.handle_put(
        url=f"/api/project/{project}/files/recording/{recording_session}/configuration",
        return_response=True,
        body=json.dumps(json_request_upload_urls_req),
    )
    if response.status_code != 200:
        print("Failed to prepare configuration upload")
        print(f"{response.text} - {response.status_code}")
        raise typer.Exit(1)

    #
    # Upload urls is a  remote_path : upload_url dict
    # '/my_config/interfaces.json' : "<upload_url>"
    #
    upload_urls = json.loads(response.text)

    # For each file - upload
    for file in track(file_infos, description="Uploading..."):
        key = file["remote_path"]
        path = file["local_path"]
        url = upload_urls[key]
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        r = requests.put(url, open(path, "rb"), headers=headers)
        if r.status_code != 200:
            print("Failed to upload broker configuration")
            print(r.status_code)
            print(r.text)
            typer.Exit(1)

    print(f"Successfully uploaded broker configuration {broker_config_dir_name}")


@app.command(help="Downloads the specified broker configuration directory as zip file")
def download_configuration(
    broker_config_name: str = typer.Argument(..., help="Broker config name"),
    recording_session: str = typer.Option(..., help="Recording session id", envvar="REMOTIVE_CLOUD_RECORDING_SESSION"),
    project: str = typer.Option(..., help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT"),
):
    rest.ensure_auth_token()
    r = rest.handle_get(
        url=f"/api/project/{project}/files/recording/{recording_session}/configuration/{broker_config_name}", return_response=True
    )
    filename = get_filename_from_cd(r.headers.get("content-disposition"))
    open(filename, "wb").write(r.content)
    print(f"Downloaded file {filename}")


@app.command(help="Downloads the specified broker configuration directory as zip file")
def delete_configuration(
    broker_config_name: str = typer.Argument(..., help="Broker config name"),
    recording_session: str = typer.Option(..., help="Recording session id", envvar="REMOTIVE_CLOUD_RECORDING_SESSION"),
    project: str = typer.Option(..., help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT"),
):
    rest.handle_delete(url=f"/api/project/{project}/files/recording/{recording_session}/configuration/{broker_config_name}")


@app.command(help="Copy recording to another project")
def copy(
    recording_session: str = typer.Argument(..., help="Recording session id"),
    project: str = typer.Option(..., help="Project to import sample recording into", envvar="REMOTIVE_CLOUD_PROJECT"),
    destination_project: str = typer.Option(..., help="Destination project"),
):
    rest.handle_post(
        url=f"/api/project/{project}/files/recording/{recording_session}/copy", body=json.dumps({"projectUid": destination_project})
    )


@app.command(deprecated=True)
def play(
    recording_session: str = typer.Argument(..., help="Recording session id", envvar="REMOTIVE_CLOUD_RECORDING_SESSION"),
    broker: str = typer.Option(None, help="Broker to use"),
    project: str = typer.Option(..., help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT"),
):
    """
    Plays a recording (Deprecated - Use recordings playback play)"
    """
    _do_change_playback_mode("play", recording_session, broker, project)


@app.command(deprecated=True)
def pause(
    recording_session: str = typer.Argument(..., help="Recording session id", envvar="REMOTIVE_CLOUD_RECORDING_SESSION"),
    broker: str = typer.Option(None, help="Broker to use"),
    project: str = typer.Option(..., help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT"),
):
    """
    Pause recording (Deprecated - Use recordings playback pause")
    """
    _do_change_playback_mode("pause", recording_session, broker, project)


@app.command(name="playback-status", deprecated=True)
def playback_status(
    recording_session: str = typer.Argument(..., help="Recording session id", envvar="REMOTIVE_CLOUD_RECORDING_SESSION"),
    broker: str = typer.Option(None, help="Broker to use"),
    project: str = typer.Option(..., help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT"),
):
    """
    Playback progress (Deprecated - Use recordings playback progress)
    """
    _do_change_playback_mode("status", recording_session, broker, project)


@app.command(deprecated=True)
def seek(
    recording_session: str = typer.Argument(..., help="Recording session id", envvar="REMOTIVE_CLOUD_RECORDING_SESSION"),
    seconds: int = typer.Option(..., min=0, help="Target offset in seconds"),
    broker: str = typer.Option(None, help="Broker to use"),
    project: str = typer.Option(..., help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT"),
):
    """
    Seek into recording (Deprecated - Use recordings playback seek)
    """
    _do_change_playback_mode("seek", recording_session, broker, project, seconds)


@app.command(deprecated=True)
def stop(
    recording_session: str = typer.Argument(..., help="Recording session id", envvar="REMOTIVE_CLOUD_RECORDING_SESSION"),
    broker: str = typer.Option(None, help="Broker to use"),
    project: str = typer.Option(..., help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT"),
):
    """
    Stop recording (Deprecated - Use recordings playback stop)
    """
    _do_change_playback_mode("stop", recording_session, broker, project)


def _do_change_playback_mode(mode: str, recording_session: str, broker: str, project: str, seconds: int | None = None):  # noqa: C901
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
    if mode == "pause":
        broker.pause_play(files, True)
    elif mode == "play":
        r = broker.play(files, True)
    elif mode == "seek":
        broker.seek(files, int(seconds * 1000000), True)
    elif mode == "stop":
        broker.seek(files, 0, True)
    elif mode == "status":
        p = Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True)
        t = p.add_task("label", total=1)

        with p:
            broker.listen_on_playback(lambda c: p.update(t, description=str(c)))
    else:
        raise Exception(f"Illegal command {mode}")


def get_filename_from_cd(cd):
    """
    Get filename from content-disposition
    """
    if not cd:
        return None
    fname = re.findall("filename=(.+)", cd)
    if len(fname) == 0:
        return None
    return fname[0]
