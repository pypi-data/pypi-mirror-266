from dataclasses import dataclass
from pathlib import Path
from uuid import UUID
from uuid import uuid4

import click
import keyring
import requests

from .constant import APP_NAME
from .constant import CONTEXT_SETTINGS
from .db import setup_db
from .models import AllInklProvider
from .models import DynDNSSetup

DB_FILE = Path(click.get_app_dir(APP_NAME, roaming=False)) / "setup_db.json"


@dataclass
class Repo:
    name: str
    uuid: UUID


pass_repo = click.make_pass_decorator(Repo)


@click.group(help="DynDNS Updater", context_settings=CONTEXT_SETTINGS)
def ddu():
    pass


@ddu.command
def list():
    with setup_db(DB_FILE) as s:
        for setup in s.setups:
            click.echo(setup.name)
            click.echo(f"  |-> UUID: {setup.uuid}")
            click.echo(f"  |-> Provider: {setup.provider.provider_type}")


@ddu.command
@click.option("-u", "--uuid", help="UUID of entry to delete", type=str, required=True)
def delete(uuid: str):

    with setup_db(DB_FILE) as setups:
        to_delete = [s for s in setups.setups if s.uuid == uuid][0]
        setups.setups.remove(to_delete)
        for c in to_delete.provider.credentials:
            keyring.delete_password(c[0], c[1])


@ddu.command
@click.option("-u", "--uuid", help="UUID of entry to delete", type=str, required=True)
def update(uuid: str) -> None:
    with setup_db(DB_FILE) as setups:
        to_update = [s for s in setups.setups if s.uuid == uuid][0]
        user = keyring.get_credential(f"ddns_{uuid}", "user")
        pwd = keyring.get_credential(f"ddns_{uuid}", "password")
        response = requests.get(to_update.provider.update_url, auth=(user, pwd))
        if response.status_code != 200:
            click.ClickException(f"Failed to access URL. Status code: {response.status_code}")


@ddu.group(help="Add a new DynDNS setup")
@click.option("-n", "--name", help="Specify a name for the setup", type=str)
@click.pass_context
def add(ctx, name: str):
    ctx.obj = Repo(name=name, uuid=uuid4())


@add.command(help="Specify ALL-INKL DynDNS setup")
@click.option("-u", "--user", type=str, prompt=True, help="DDNS user")
@click.option("-p", "--password", type=str, prompt=True, hide_input=True, help="DDNS password")
@pass_repo
def all_inkl(repo: Repo, user: str, password: str):
    setup = DynDNSSetup(
        name=repo.name,
        uuid=str(repo.uuid),
        provider=AllInklProvider(
            credentials=[(f"ddns_{repo.uuid}", "user"), (f"ddns_{repo.uuid}", "password")]
        ),
    )
    keyring.set_password(f"ddns_{setup.uuid}", "user", user)
    keyring.set_password(f"ddns_{setup.uuid}", "password", password)
    with setup_db(DB_FILE) as s:
        s.setups.append(setup)
