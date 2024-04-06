from typing import Optional

import click

from mlfoundry import env_vars
from mlfoundry.login import login as login_


@click.command(short_help="Store API key in the local file system")
@click.option(
    "--host",
    "--tracking-uri",
    "--tracking_uri",
    "tracking_uri",
    type=click.STRING,
    required=True,
    envvar=env_vars.TRACKING_HOST_GLOBAL,
    help="Tracking server host (URL to Truefoundry platform)",
)
@click.option(
    "--relogin",
    is_flag=True,
    show_default=True,
    default=False,
    help="Overwrite existing API key for the given `--host`/`--tracking_uri`",
)
@click.option(
    "--api-key",
    "--api_key",
    type=click.STRING,
    default=None,
    prompt="Please enter an API Key",
    hide_input=True,
    prompt_required=False,
)
def login(tracking_uri: Optional[str], relogin: bool, api_key: Optional[str]):
    login_(tracking_uri=tracking_uri, relogin=relogin, api_key=api_key)
