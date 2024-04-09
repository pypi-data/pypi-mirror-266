import sys

from typing_extensions import Annotated

from rich import print
from rich.panel import Panel
from typer import Argument, Option, Typer

from arkhos.base_handler import base_handler

app = Typer(add_completion=False)


@app.command()
def main(
    method: Annotated[
        str, Argument(help="Arkhos request type: GET, POST, CRON, EMAIL")
    ] = "GET",
    get: Annotated[str, Option(help="?key_1=value_1&key_2=value_2")] = "",
    path: Annotated[str, Option(help="/path/to/thing")] = "/",
    body: Annotated[str, Option(help='"the HTTP request or email body"')] = "",
    headers: Annotated[str, Option(help="{'key_1': 'value_1', ...}")] = "",
    subject: Annotated[str, Option(help='"the email subject"')] = "",
):
    """Test your Arkhos app locally.


    arkhos <method> --get key_1=value&key_2=value_2 --body an_optional request body --headers "{key_1: value_1,...}"
    """
    response = base_handler(
        {
            "method": method,
            "path": path,
        }
    )
    body = response.get("body", "")
    status = response.get("status")
    status_color = "green" if status == 200 else "red"
    if not sys.stdout.isatty():
        print(body)
    else:
        print(
            Panel(
                body,
                title=f"[purple]{method.upper()} [{status_color}]{status}",
                title_align="left",
                subtitle="[purple]Arkhos",
                subtitle_align="right",
            )
        )
