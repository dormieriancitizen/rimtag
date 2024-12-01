import logging, json, requests
from typing import Any
from urllib.parse import urlparse
from pathlib import Path


from mod_manager.mod_handler import Mod

def compile_rentry(mods: dict[Path, Mod]):
    report = (
        f"# RimWorld Mod List: {len(mods)} mods       ![](https://github.com/RimSort/RimSort/blob/main/docs/rentry_preview.png?raw=true)"
        "\nCreated with a bad python script with a lot of borrowed code from RimSort"
        f"\nMod list was created for game version: {Path("/home/dormierian/Games/rimworld/"+'Version.txt').read_text()}"
        "\n\nLocal mods are marked as yellow labels with packageid in brackets."
        "\nMods not from the current version are marked in red"
        f"\n!!! note Mod list length: `{len(mods)}`\n"
        "\n***"
        "\n# | Mod Name | Info"
        "\n:-: | ------ | :------:"

    )

    count = 0

    for _, mod in mods.items():
        pfid = ""
        line = ""

        count += 1
        name = mod.name

        url = mod.download_link

        pid = mod.pid

        line += "\n"
        package_id_string = "{packageid: " + pid + "}"

        # if getenv("RIMWORLD_VERSION") not in modd[mod]["supportedVersions"]:
        #     line += "\n!!! danger "
        # elif modd[mod]["source"] in ("LOCAL","GIT"):
        #     line += ""
        # elif modd[mod]["source"] == "LUDEON":
        #     line += "\n!!! info "
        # elif modd[mod]["source"] == "STEAM":
        #     pass

        # Add the index
        line += str(count) + '.|'

        pfid = mod.pfid

        if pfid:
            # Image
            line += f"![{pid}]({pfid})"+"{100px:56px} "
        
        if not url:
            line += f" {name}"  # f-strings don't support the squilly brackets
        else:
            line += f" [{name}]({url})"

        if mod.source == "LOCAL":
            line += " "+package_id_string   

        line += f"| {mod.best_supported_version()}" #, {"XML" if modd[mod]["xml_only"] else "C#"}"
        report += line

    return report

def upload(text: str):
    rentry_uploader = RentryUpload(text)
    successful = rentry_uploader.upload_success
    host = urlparse(rentry_uploader.url).hostname if successful else None
    if rentry_uploader.url and host and host.endswith("rentry.co"):  # type: ignore
        pass

# Taken wholly from RimPy
BASE_URL = "https://rentry.co"
BASE_URL_RAW = f"{BASE_URL}/raw"
API_NEW_ENDPOINT = f"{BASE_URL}/api/new"
_HEADERS = {"Referer": BASE_URL}

class HttpClient:
    def __init__(self) -> None:
        # Initialize a session for making HTTP requests
        self.session = requests.Session()

    def make_request(
        self,
        method: str,
        url: str,
        data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> requests.Response:
        # Perform a HTTP request and return the response
        headers = headers or {}
        request_method = getattr(self.session, method.lower())
        response = request_method(url, data=data, headers=headers)
        response.data = response.text
        return response

    def get(self, url: str, headers: dict[str, str] | None = None) -> requests.Response:
        return self.make_request("GET", url, headers=headers)

    def post(
        self,
        url: str,
        data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> requests.Response:
        return self.make_request("POST", url, data=data, headers=headers)

    def get_csrf_token(self) -> str | None:
        # Get CSRF token from the response cookies after making a GET request to the base URL
        response = self.get(BASE_URL)
        return response.cookies.get("csrftoken")


class RentryUpload:
    def __init__(self, text: str):
        self.upload_success = False
        self.url = None
        self.logger = logging.getLogger()

        try:
            response = self.new(text)
            if response.get("status") != "200":
                self.handle_upload_failure(response)
            else:
                self.upload_success = True
                self.url = response["url"]
        finally:
            if self.upload_success:
                self.logger.info(f"RentryUpload successfully uploaded data! Url: {self.url}\nEdit code: {response['edit_code']}")

    def handle_upload_failure(self, response: dict[str, Any]) -> None:
        """
        Log and handle upload failure details.
        """
        error_content = response.get("content", "Unknown")
        errors = response.get("errors", "").split(".")
        for error in errors:
            self.logger.error(error)

        self.logger.error("RentryUpload failed!")

    def new(self, text: str):
        """
        Upload new entry to Rentry.co.
        """
        # Initialize an HttpClient for making HTTP requests
        client = HttpClient()

        # Get CSRF token for authentication
        csrf_token = client.get_csrf_token()

        # Prepare payload for the POST request
        payload = {
            "csrfmiddlewaretoken": csrf_token,
            "text": text,
        }

        # Perform the POST request to create a new entry
        return json.loads(
            client.post(API_NEW_ENDPOINT, data=payload, headers=_HEADERS).text
        )