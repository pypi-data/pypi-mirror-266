from __future__ import annotations

import base64
import json
import logging
import os
import shutil
from importlib.metadata import version
from pathlib import Path
from typing import Dict, List, Union

import requests
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, wrap_file

from cli import settings

err_console = Console(stderr=True)

if "REMOTIVE_CLOUD_HTTP_LOGGING" in os.environ:
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True
global baseurl
global license_server_base_url
base_url = "https://cloud.remotivelabs.com"
license_server_base_url = "https://license.cloud.remotivelabs.com"

if "REMOTIVE_CLOUD_BASE_URL" in os.environ:
    base_url = os.environ["REMOTIVE_CLOUD_BASE_URL"]

if "cloud-dev" in base_url:
    license_server_base_url = "https://license.cloud-dev.remotivelabs.com"

# if 'REMOTIVE_CLOUD_AUTH_TOKEN' not in os.environ:
#    print('export REMOTIVE_CLOUD_AUTH_TOKEN=auth must be set')
#    exit(0)

# token = os.environ["REMOTIVE_CLOUD_AUTH_TOKEN"]
# headers = {"Authorization": "Bearer " + token}

headers = {}
org = ""

token = ""

cli_version = version("remotivelabs-cli")


def ensure_auth_token():
    global token

    # if 'REMOTIVE_CLOUD_ORGANISATION' not in os.environ:
    #    print('You must first set the organisation id to use: export REMOTIVE_CLOUD_ORGANISATION=organisationUid')
    #    raise typer.Exit()
    global org
    # org = os.environ["REMOTIVE_CLOUD_ORGANISATION"]

    #    if not exists(str(Path.home()) + "/.config/.remotive/cloud.secret.token"):
    #        print("Access token not found, please login first")
    #        raise typer.Exit()

    #    f = open(str(Path.home()) + "/.config/.remotive/cloud.secret.token", "r")
    token = settings.read_token()
    #    os.environ['REMOTIVE_CLOUD_AUTH_TOKEN'] = token
    global headers

    headers["Authorization"] = "Bearer " + token.strip()
    headers["User-Agent"] = f"remotivelabs-cli {cli_version}"


def handle_get(
    url,
    params=None,
    return_response: bool = False,
    allow_status_codes=None,
    progress_label="Fetching...",
    use_progress_indicator: bool = True,
    timeout: int = 20,
):
    if params is None:
        params = {}
    ensure_auth_token()
    if use_progress_indicator:
        with use_progress(progress_label):
            r = requests.get(f"{base_url}{url}", headers=headers, params=params, timeout=timeout)
    else:
        r = requests.get(f"{base_url}{url}", headers=headers, params=params, timeout=timeout)

    if return_response:
        check_api_result(r, allow_status_codes)
        return r
    print_api_result(r)


def has_access(url, params={}):
    ensure_auth_token()
    r = requests.get(f"{base_url}{url}", headers=headers, params=params)
    if r.status_code == 401:
        return False
    return True


def check_api_result(response, allow_status_codes: List[int] = None):
    if response.status_code > 299:
        if allow_status_codes is not None and response.status_code in allow_status_codes:
            return
        err_console.print(f":boom: [bold red]Got status code[/bold red]: {response.status_code}")
        if response.status_code == 401:
            err_console.print("Your token has expired, please login again")
        else:
            err_console.print(response.text)
        exit(1)


def print_api_result(response):
    if response.status_code >= 200 and response.status_code < 300:
        if len(response.content) > 4:
            print(json.dumps(response.json()))
        exit(0)
    else:
        err_console.print(f":boom: [bold red]Got status code[/bold red]: {response.status_code}")
        if response.status_code == 401:
            err_console.print("Your token has expired, please login again")
        else:
            err_console.print(response.text)
        exit(1)
    # typer.Exit(1) did not work as expected


def handle_delete(url, params={}, quiet=False, success_msg="Successfully deleted", progress_label="Deleting..."):
    ensure_auth_token()
    with use_progress(progress_label):
        r = requests.delete(f"{base_url}{url}", headers=headers, params=params)
    if r.status_code == 200 or r.status_code == 204:
        if not quiet:
            print_api_result(r)
    else:
        print_api_result(r)


def handle_post(url, body=None, params={}, progress_label: str = "Processing...", return_response: bool = False):
    ensure_auth_token()
    headers["content-type"] = "application/json"

    with use_progress(progress_label):
        r = requests.post(f"{base_url}{url}", headers=headers, params=params, data=body)

    if return_response:
        check_api_result(r)
        return r

    print_api_result(r)


def handle_put(url, body=None, params={}, return_response: bool = False):
    ensure_auth_token()
    headers["content-type"] = "application/json"
    r = requests.put(f"{base_url}{url}", headers=headers, params=params, data=body)

    if return_response:
        check_api_result(r)
        return r
    print_api_result(r)


def upload_file(
    path: Union[str, Path], url: str, upload_headers: dict[str, str] = None, return_response: bool = False, progress_label="Uploading..."
):
    ensure_auth_token()
    if upload_headers is not None:
        headers.update(upload_headers)
    with open(path, "rb") as file:
        with wrap_file(file, os.stat(path).st_size, description=progress_label) as f:
            r = requests.post(f"{base_url}{url}", files={os.path.basename(path): f}, headers=headers)
        if return_response:
            check_api_result(r)
            return r
        print_api_result(r)


def upload_file_with_signed_url(
    path: Union[str, Path], url: str, upload_headers: dict[str, str], return_response: bool = False, progress_label="Uploading..."
):
    with open(path, "rb") as file:
        with wrap_file(file, os.stat(path).st_size, description=progress_label) as f:
            r = requests.put(url, data=f, headers=upload_headers)
        if return_response:
            check_api_result(r)
            return r
        print_api_result(r)


def use_progress(label: str):
    p = Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True)
    p.add_task(label, total=1)
    return p


def download_file(save_file_name: str, url: str):
    # Next download the actual file
    download_resp = requests.get(url=url, stream=True)
    if download_resp.status_code == 200:
        content_length = int(download_resp.headers["Content-Length"])
        with open(save_file_name, "wb") as out_file:
            with wrap_file(download_resp.raw, content_length, refresh_per_second=100) as stream_with_progress:
                shutil.copyfileobj(stream_with_progress, out_file)
    else:
        check_api_result(download_resp)


def request_license(email: str, machine_id: Dict[str, any]) -> str:
    # Lets keep the email here so we have the same interface for both authenticated
    # and not authenticated license requests.
    # email will be validated in the license server to make sure it matches with the user of the
    # access token so not any email is sent here
    ensure_auth_token()
    payload = {"id": email, "machine_id": machine_id}
    b64_encoded_bytes = base64.encodebytes(json.dumps(payload).encode())
    license_jsonb64 = {"licensejsonb64": b64_encoded_bytes.decode("utf-8")}
    headers["content-type"] = "application/json"
    r = requests.post(url=f"{license_server_base_url}/api/license/request", headers=headers, data=json.dumps(license_jsonb64))
    check_api_result(r)
    return r.json()["license_data"]
