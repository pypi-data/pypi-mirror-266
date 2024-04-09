#pyright: reportPrivateImportUsage=false
from collections import defaultdict
import functools
import io
import re
import shlex
from typing import Sequence, cast, Any, List
from click.core import Context
from click.formatting import HelpFormatter
import requests
import datetime

from relationalai.clients import azure
from relationalai.errors import RelQueryError
from relationalai.loaders.types import LoadType, UnsupportedTypeError
from relationalai.loaders.csv import CSVLoader
from relationalai.loaders.loader import Loader, rel_schema_to_type
from ..clients.types import ImportSource, ImportSourceFile, ImportSourceTable
from ..clients.client import ResourceProvider
from .. import Resources
import rich
from rich.console import Console
from rich import box as rich_box
from rich.table import Table
from ..tools import debugger as deb
from ..clients import config, snowflake
from ..clients.config import (
    FIELD_PLACEHOLDER,
    ConfigFile,
    all_configs_including_legacy,
    get_from_snowflake_connections_toml,
    azure_default_props,
    snowflake_default_props,
)
from InquirerPy.base.control import Choice

import os
import sys
import click
from pathlib import Path
from .cli_controls import divider, Spinner
from . import cli_controls as controls

#--------------------------------------------------
# Constants
#--------------------------------------------------

ENGINE_SIZES = ["XS", "S", "M", "L", "XL"]
PROFILE = None

SNOWFLAKE = "Snowflake"
AZURE = "Azure (Beta)"

AZURE_ENVS = {
    "Production": {
        "host": "azure.relationalai.com",
        "client_credentials_url": "https://login.relationalai.com/oauth/token"
    },
    "Early Access": {
        "host": "azure-ea.relationalai.com",
        "client_credentials_url": "https://login-ea.relationalai.com/oauth/token"
    },
    "Staging": {
        "host": "azure-staging.relationalai.com",
        "client_credentials_url": "https://login-staging.relationalai.com/oauth/token"
    },
    "Latest": {
        "host": "azure-latest.relationalai.com",
        "client_credentials_url": "https://login-latest.relationalai.com/oauth/token"
    },
}

#--------------------------------------------------
# Helpers
#--------------------------------------------------

@functools.cache
def get_config(profile:str|None = None):
    global PROFILE
    return config.Config(profile or PROFILE)

@functools.cache
def get_resource_provider(platform:str|None=None, _cfg:config.Config|None = None) -> ResourceProvider:
    cfg = _cfg or get_config()
    provider = Resources(config=cfg)
    return provider

def supports_platform(*platform_names: str):
    def decorator(cmd: click.Command):
        setattr(cmd, "__available_platforms", platform_names)
        cb = cmd.callback
        assert cb
        def checked(*args, **kwargs):
            assert cmd.name
            assert_command_available(cmd.name, command_available(cmd))
            return cb(*args, **kwargs)

        cmd.callback = checked
        return cmd
    return decorator

def command_available(cmd: click.Command) -> bool:
    available_platforms = getattr(cmd, "__available_platforms", ())
    platform = get_config().get("platform", "")
    return not available_platforms or not platform or platform in available_platforms

def assert_command_available(name: str, available: bool, plural=False):
    if not available:
        platform = get_config().get("platform", "")
        rich.print(f"[yellow]{name} {'are' if plural else 'is'} not available for {platform}")
        divider()
        sys.exit(1)

def coming_soon():
    rich.print("[yellow]This isn't quite ready yet, but it's coming soon!")
    divider()
    sys.exit(1)

def ensure_config(profile:str|None=None) -> config.Config:
    cfg = get_config(profile)
    if not cfg.file_path:
        rich.print("[yellow bold]No configuration file found.")
        rich.print("To create one, run: [green bold]rai init[/green bold]")
        divider()
        sys.exit(1)
    return cfg

#--------------------------------------------------
# Custom help printer
#--------------------------------------------------

class RichGroup(click.Group):
    def format_help(self, ctx: Context, formatter: HelpFormatter) -> None:
        global PROFILE
        # @NOTE: I couldn't find a sane way to access the --profile option from here, so insane it is.
        if "--profile" in sys.argv:
            ix = sys.argv.index("--profile") + 1
            if ix < len(sys.argv):
                PROFILE = sys.argv[ix]

        profile = get_config().profile
        if profile == "__top_level__":
            profile = "[yellow bold]None[/yellow bold]" if not get_config().get("platform", "") else "[ROOT]"

        sio = io.StringIO()
        console = Console(file=sio, force_terminal=True)
        divider(console)
        console.print("[bold]Welcome to [green]RelationalAI![/bold]")
        console.print()
        console.print("rai [magenta]\\[options][/magenta] [cyan]command[/cyan]")

        console.print()
        console.print(f"[magenta]--profile[/magenta][dim] - which config profile to use (current: [/dim][cyan]{profile}[/cyan][dim])")

        unavailable_commands = []
        groups = defaultdict(list)
        for command in self.commands.keys():
            if ":" in command:
                group, _, _ = command.rpartition(":")
                groups[group].append(command)
            else:
                groups[""].append(command)

        console.print()
        for command in groups[""]:
            console.print(f"[cyan]{command}[/cyan][dim] - {self.commands[command].help}")

        for group, commands in groups.items():
            if not group:
                continue

            empty = True
            for command in commands:
                if command_available(self.commands[command]):
                    if empty:
                        empty = False
                        console.print()

                    console.print(f"[cyan]{command}[/cyan][dim] - {self.commands[command].help}")
                else:
                    unavailable_commands.append(command)

        if unavailable_commands:
            platform = get_config().get("platform", "")
            console.print()
            console.print(f"[yellow]Not available on {platform}[/yellow]")
            console.print()
            for command in unavailable_commands:
                console.print(f"[dim yellow]{command} - {self.commands[command].help}")

        divider(console)
        formatter.write(sio.getvalue())
        sio.close()

#--------------------------------------------------
# Custom Click Option and Argument Types
#--------------------------------------------------

ImportOption = tuple[list[str], str]

class ImportOptionsType(click.ParamType):
    def __init__(self):
        self.options = {}

    name ="import_options"
    def convert(self, raw, param, ctx) -> ImportOption:
        if ':' not in raw or '=' not in raw:
            self.fail(f"'{raw}' is not a valid import option.", param, ctx)
        raw_key, val = raw.split('=', 1)
        if len(val) == 2 and val[0] == "\\":
            val = val.encode().decode("unicode_escape")
        return (raw_key.split(":"), val)

    @classmethod
    def reduce(cls, kvs:Sequence[ImportOption]):
        options = {}
        for (key_parts, val) in kvs:
            cur = options
            for part in key_parts[:-1]:
                cur = cur.setdefault(part, {})
            cur[key_parts[-1]] = val
        return options

#--------------------------------------------------
# Main group
#--------------------------------------------------

@click.group(cls=RichGroup)
@click.option("--profile", help="Which config profile to use")
def cli(profile):
    global PROFILE
    PROFILE = profile

#--------------------------------------------------
# Init
#--------------------------------------------------

@cli.command(help="Initialize a new project")
def init():
    init_flow()

#--------------------------------------------------
# Init flow
#--------------------------------------------------

def azure_flow(cfg:config.Config):
    option_selected = check_original_config_flow(cfg, "azure")
    # get the client id and secret
    client_id = controls.text("Client ID:", default=cfg.get("client_id", "") if option_selected else "")
    client_secret = controls.password("Client Secret:", default=cfg.get("client_secret", "") if option_selected else "")
    host = cfg.get("host", "")
    client_credentials_url = cfg.get("client_credentials_url", "")
    if not host or not client_credentials_url:
        env = controls.fuzzy("Select environment:", [*AZURE_ENVS.keys(), "<custom>"])
        if env == "<custom>":
            host = controls.text("Host:")
            client_credentials_url = controls.text("Client Credentials URL:")
        else:
            host = AZURE_ENVS[env]["host"]
            client_credentials_url = AZURE_ENVS[env]["client_credentials_url"]
    # setup the default config
    cfg.fill_in_with_azure_defaults(
        client_id=client_id,
        client_secret=client_secret,
        host=host if host else None,
        client_credentials_url=client_credentials_url if client_credentials_url else None
    )

def unexpand_user_path(path):
    """Inverse of os.path.expanduser"""
    home_dir = os.path.expanduser('~')
    if path.startswith(home_dir):
        return '~' + path[len(home_dir):]
    return path

def account_from_url(account_or_url:str):
    regex = r"https://app.snowflake.com/([^/]+)/([^/]+)/.*"
    match = re.match(regex, account_or_url)
    if match:
        org = match.group(1)
        account = match.group(2)
        return f"{org}-{account}"
    else:
        return account_or_url

def snowflake_flow(cfg:config.Config):
    pyrel_config = check_original_config_flow(cfg, "snowflake")
    if not pyrel_config:
        check_snowflake_connections_flow(cfg)
    # get account info
    user = controls.text("SnowSQL user:", default=cfg.get("user", ""))
    cfg.set("user", user)
    password = controls.password("SnowSQL password:", default=cfg.get("password", ""))
    cfg.set("password", password)
    rich.print("\n[dim]  Note: Account ID should look like: myorg-account123")
    rich.print("[dim]  Details: https://docs.snowflake.com/en/user-guide/admin-account-identifier\n")
    rich.print("[dim]  Alternatively, you can log in to Snowsight, copy the URL, and paste it here.")
    rich.print("[dim]  Example: https://app.snowflake.com/myorg/account123/worksheets\n")
    account_or_url = controls.text("Snowflake account:", default=cfg.get("account", ""))
    account = account_from_url(account_or_url)
    if "." in account:
        rich.print("\n[yellow] Your Account ID should not contain a period (.) character.")
        corrected_account = account.replace(".", "-")
        use_replacement = controls.confirm(f"Use '{corrected_account}' instead", default=True)
        if use_replacement:
            account = corrected_account
    if account_or_url != account:
        rich.print(f"\n[dim]  Account ID: {account}")
    cfg.set("account", account)
    # setup the default config
    cfg.fill_in_with_snowflake_defaults(
        user=user,
        password=password,
        account=account,
    )

def filter_profiles_by_platform(config:ConfigFile, platform:str):
    filtered_config = {}
    for profile, props in config.get_combined_profiles().items():
        if profile == "__top_level__":
            continue
        if props.get("platform") == platform or (
            props.get("platform") is None
            and platform == "azure"
        ):
            filtered_config[profile] = props
    return filtered_config

def check_original_config_flow(cfg:config.Config, platform:str):
    all_profiles = {}
    for config_file in all_configs_including_legacy():
        file_path = config_file.path
        plt_config = filter_profiles_by_platform(config_file, platform)
        for profile, props in plt_config.items():
            profile_id = (profile, file_path)
            all_profiles[profile_id] = props
    if platform == "snowflake":
        sf_config = get_from_snowflake_connections_toml()
        if sf_config:
            file_path = os.path.expanduser("~/.snowflake/connections.toml")
            for profile, props in sf_config.items():
                profile_id = (profile, file_path)
                all_profiles[profile_id] = props
    if len(all_profiles) == 0:
        return
    max_profile_name_len = max(len(profile) for profile, _ in all_profiles.keys())
    profile_options: List[Choice] = []
    for profile, props in all_profiles.items():
        formatted_name = f"{profile[0]:<{max_profile_name_len}}  {unexpand_user_path(profile[1])}"
        profile_options.append(Choice(value=profile, name=formatted_name))
    selected_profile = controls.select("Use existing profile", list(profile_options), None, mandatory=False)
    if not selected_profile:
        return
    cfg.profile = selected_profile[0]
    cfg.update(all_profiles[selected_profile])
    return True

def check_snowflake_connections_flow(cfg:config.Config):
    sf_config = get_from_snowflake_connections_toml()
    if not sf_config or len(sf_config) == 0:
        return
    profiles = list(sf_config.keys())
    if len(profiles) == 0:
        return
    profile = controls.fuzzy("Use profile from ~/.snowflake/connections.toml", profiles, mandatory=False)
    if not profile:
        return
    cfg.profile = profile
    cfg.update(sf_config[profile])
    return True

def get_default(value:str|None, list_of_values:Sequence[str]):
    if value is None:
        return None
    list_of_values_lower = [v.lower() for v in list_of_values]
    value_lower = value.lower()
    if value_lower in list_of_values_lower:
        return value

def role_flow(provider:ResourceProvider, cfg:config.Config):
    with Spinner("Fetching roles", "Fetched roles"):
        try:
            roles = cast(snowflake.Resources, provider).list_roles()
        except Exception as e:
            raise Exception(f"Error fetching roles: {e}")
    role_names = [r["name"] for r in roles]
    if len(role_names) == 0:
        raise Exception("No roles found")
    default = get_default(cfg.get("role", None), role_names)
    role = controls.fuzzy("Select a role:", role_names, default=default, mandatory=False)
    cfg.set("role", role or FIELD_PLACEHOLDER)
    provider.reset()

def warehouse_flow(provider:ResourceProvider, cfg:config.Config):
    rich.print("")
    with Spinner("Fetching warehouses", "Fetched warehouses"):
        try:
            warehouses = cast(snowflake.Resources, provider).list_warehouses()
        except Exception as e:
            raise Exception(f"Error fetching warehouses: {e}")
    rich.print("")
    warehouse_names = [w["name"] for w in warehouses]
    if len(warehouse_names) == 0:
        raise Exception("No warehouses found")
    default = get_default(cfg.get("warehouse", None), warehouse_names)
    warehouse = controls.fuzzy("Select a warehouse:", warehouse_names, default=default, mandatory=False)
    cfg.set("warehouse", warehouse or FIELD_PLACEHOLDER)

def rai_app_flow(provider:ResourceProvider, cfg:config.Config):
    rich.print("")
    with Spinner("Fetching installed apps", "Fetched apps"):
        try:
            apps = cast(snowflake.Resources, provider).list_apps()
        except Exception as e:
            raise Exception(f"Error fetching apps: {e}")
    rich.print("")
    app_names = [w["name"] for w in apps]
    if len(app_names) == 0:
        raise Exception("No apps found")
    default = get_default(cfg.get("rai_app_name", None), app_names)
    app = controls.fuzzy("Select RelationalAI app name:", app_names, default=default, mandatory=False)
    cfg.set("rai_app_name", app or FIELD_PLACEHOLDER)
    provider.reset()

def spcs_flow(provider: ResourceProvider, cfg: config.Config):

    role_flow(provider, cfg)
    warehouse_flow(provider, cfg)
    rai_app_flow(provider, cfg)

def engine_flow(provider:ResourceProvider, cfg:config.Config):
    rich.print("")
    with Spinner("Fetching engines", "Fetched engines"):
        try:
            engines = provider.list_engines()
        except Exception as e:
            raise Exception(f"Error fetching engines: {e}")

    engine_names = ["Create a new engine"] + [engine.get("name") for engine in engines]
    rich.print("")
    default = get_default(cfg.get("engine", None), engine_names)
    engine = controls.fuzzy("Select an engine:", choices=engine_names, default=default, mandatory=False)
    if engine == "Create a new engine":
        engine = controls.text("Engine name:")
        engine_size = controls.fuzzy("Engine size:", choices=ENGINE_SIZES)
        engine_pool = ""
        if cfg.get("platform") == "snowflake":
            provider = cast(snowflake.Resources, provider)
            rich.print("")
            with Spinner("Fetching compute pools", "Fetched compute pools"):
                try:
                    pools = [v["name"] for v in provider.list_compute_pools()]
                except Exception as e:
                    raise Exception(f"Error fetching compute pools: {e}")
            if len(pools) == 0:
                raise Exception("No compute pools found")
            rich.print("")
            engine_pool = controls.fuzzy("Compute pool:", pools, mandatory=False)
        rich.print("")
        with Spinner(f"Creating '{engine}' engine... (this may take several minutes)", f"Engine '{engine}' created"):
            try:
                provider.create_engine(engine, engine_size, engine_pool)
            except Exception as e:
                raise Exception(f"Error creating engine: {e}")
        rich.print("")
    cfg.set("engine", engine or FIELD_PLACEHOLDER)

def gitignore_flow():
    current_dir = Path.cwd()
    prev_dir = None
    while current_dir != prev_dir:
        gitignore_path = current_dir / '.gitignore'
        if gitignore_path.exists():
            # if there is, check to see if raiconfig.toml is in it
            with open(gitignore_path, 'r') as gitignore_file:
                if 'raiconfig.toml' in gitignore_file.read():
                    return
                else:
                    # if it's not, ask to add it
                    add_to_gitignore = controls.confirm("Add raiconfig.toml to .gitignore?", default=True)
                    if add_to_gitignore:
                        with open(gitignore_path, 'a') as gitignore_file:
                            gitignore_file.write("\nraiconfig.toml")
                    return
        prev_dir = current_dir
        current_dir = current_dir.parent

def save_flow(cfg:config.Config, confirmed:bool=False):
    if cfg.profile in cfg.get_profiles():
        if not controls.confirm(f"Overwrite existing {cfg.profile} profile"):
            profile_name = controls.text("Profile name:")
            if profile_name:
                cfg.profile = profile_name
            else:
                save_flow(cfg)
                return
    cfg.save()

def init_flow():
    cfg = config.Config(fetch=False)
    try:
        cfg.clone_profile()
        rich.print("\n[dim]---------------------------------------------------\n")
        rich.print("[bold]Welcome to [green]RelationalAI!\n")
        rich.print("Press Control-S to skip a prompt\n")

        platform = controls.fuzzy("Host platform:", choices=[SNOWFLAKE, AZURE])
        cfg.set("platform", {
            SNOWFLAKE: "snowflake",
            AZURE: "azure"
        }[platform])

        if platform == SNOWFLAKE:
            snowflake_flow(cfg)
        elif platform == AZURE:
            azure_flow(cfg)
        elif platform:
            rich.print("[yellow]Initialization aborted!")
            rich.print(f"[yellow]Unknown platform: {platform}")
            return

        provider = get_resource_provider(None, cfg)

        rich.print()
        if platform == SNOWFLAKE:
            spcs_flow(provider, cfg)
        engine_flow(provider, cfg)
        save_flow(cfg)

        gitignore_flow()
        rich.print("")
        rich.print("[green]✓ raiconfig.toml saved!")
        rich.print("\n[dim]---------------------------------------------------\n")
    except Exception as e:
        rich.print("")
        rich.print("[yellow bold]Initialization aborted!")
        rich.print(f"[yellow]{e}")
        print(e.with_traceback(None))
        rich.print("")

        save = controls.confirm("Save partial config?")
        if save:
            rich.print("")
            cfg.fill_in_with_defaults()
            save_flow(cfg)
            gitignore_flow()
            rich.print(f"[yellow bold]✓ Saved partial raiconfig.toml ({os.path.abspath('raiconfig.toml')})")

        divider()

#--------------------------------------------------
# Explain config
#--------------------------------------------------

@cli.command(
    name="config:explain",
    help="Inspect config status",
)
@click.option(
    "--profile",
    help="Profile to inspect",
)
@click.option(
    "--all-profiles",
    help="Whether to show all profiles in config file",
    is_flag=True,
)
def config_explain(profile:str="default", all_profiles:bool=False):
    divider()
    cfg = ensure_config(profile)

    rich.print(f"[bold green]{cfg.file_path}")
    if os.getenv("RAI_PROFILE"):
        rich.print(f"[yellow]Environment variable [bold]RAI_PROFILE = {os.getenv('RAI_PROFILE')}[/bold]")
    rich.print("")
    if cfg.profile != "__top_level__":
        rich.print(f"[bold]\\[{cfg.profile}]")

    for key, value in cfg.items():
        if key == "active_profile" and cfg.profile != "__top_level__":
            continue
        rich.print(f"{key} = [cyan bold]{mask(key, value)}")

    platform = cfg.get("platform", "snowflake")
    defaults = snowflake_default_props if platform == "snowflake" else azure_default_props

    for key, value in defaults.items():
        if key not in cfg:
            rich.print(f"[yellow bold]{key}[/yellow bold] = ?" + (
                f" (default: {value})" if value and value != FIELD_PLACEHOLDER else ""
            ))

    if all_profiles:
        for profile, props in cfg.get_profiles().items():
            if profile == cfg.profile:
                continue
            if len(props):
                rich.print()
                rich.print(f"[bold]\\[{profile}][/bold]")
                for key, value in props.items():
                    rich.print(f"{key} = [cyan bold]{mask(key, value)}")

    divider()

def mask(key: str, value: Any):
    if key in ["client_secret", "password"]:
        return "*" * len(str(value))
    return value

#--------------------------------------------------
# Check config
#--------------------------------------------------

@cli.command(
    name="config:check",
    help="Check whether config is valid",
)
def config_check(all_profiles:bool=False):
    divider()
    ensure_config()
    with Spinner("Connecting to platform..."):
        try:
            get_resource_provider().list_engines()
        except Exception as e:
            rich.print(f"[yellow]Error: {e}")
            divider()
            sys.exit(1)
    rich.print("[green]✓ Connection successful!")

#--------------------------------------------------
# Version
#--------------------------------------------------


def latest_version(package_name):
    """Get the current version of a package on PyPI."""
    url = f"https://pypi.org/pypi/{package_name}/json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        version = data['info']['version']
        return version
    else:
        return None

@cli.command(help="Print version info")
def version():
    from .. import __version__
    from railib import __version__ as railib_version

    table = Table(show_header=False, border_style="dim", header_style="bold", box=rich_box.SIMPLE)
    def print_version(name, version, latest=None):
        if latest is not None and version != latest:
            table.add_row(f"[bold]{name}[red]", f"[red bold]{version} → {latest}")
        else:
            table.add_row(f"[bold]{name}", f"[green]{version}")

    divider()
    print_version("RelationalAI", __version__, latest_version("relationalai"))
    print_version("Rai-sdk", railib_version, latest_version("rai-sdk"))

    if get_config().get("platform") == "snowflake":
        # print()
        with Spinner("Checking app version"):
            try:
                app_version = get_resource_provider().get_version()
            except Exception as e:
                rich.print(f"\n\n[yellow]Error fetching app version: {e}")
                exit(1)
        print_version("App", app_version)

    print_version("Python", sys.version.split()[0])

    rich.print(table)
    divider()

#--------------------------------------------------
# Debugger
#--------------------------------------------------

@cli.command(help="Open the RAI debugger")
@click.option("--port", help="Port to use", default=8080)
def debugger(port):
    deb.main(port)

#--------------------------------------------------
# Engine list
#--------------------------------------------------

@cli.command(name="engines:list", help="List all engines")
def engines_list():
    divider(flush=True)
    ensure_config()
    with Spinner("Fetching engines"):
        try:
            engines = get_resource_provider().list_engines()
        except Exception as e:
            rich.print(f"\n\n[yellow]Error fetching engines: {e}")
            exit(1)

    if len(engines):
        table = Table(show_header=True, border_style="dim", header_style="bold", box=rich_box.SIMPLE_HEAD)
        table.add_column("Name")
        table.add_column("Size")
        table.add_column("State")
        for engine in engines:
            table.add_row(engine.get("name"), engine.get("size"), engine.get("state"))
        rich.print(table)
    else:
        rich.print("[yellow]No engines found")

    divider()

#--------------------------------------------------
# Engine create
#--------------------------------------------------

@cli.command(name="engines:create", help="Create a new engine")
@click.option("--name", help="Name of the engine")
@click.option("--size", type=click.Choice(ENGINE_SIZES, case_sensitive=False), help="Size of the engine")
def engines_create(name, size):
    divider(flush=True)
    ensure_config()
    name = controls.prompt("Engine name?", name, newline=True)
    if not size:
        size = controls.fuzzy("Engine size:", choices=ENGINE_SIZES)
        rich.print("")
    provider = get_resource_provider()

    if provider.config.get("platform") == "snowflake":
        provider = cast(snowflake.Resources, provider)
        rich.print("")
        with Spinner("Fetching compute pools", "Fetched compute pools"):
            try:
                pools = [v["name"] for v in provider.list_compute_pools()]
            except Exception as e:
                rich.print(f"\n\n[yellow]Error fetching compute pools: {e}")
                exit(1)
        if len(pools) == 0:
            raise Exception("No compute pools found")
        rich.print("")
        pool = controls.fuzzy("Compute pool:", pools)
        rich.print("")
    else:
        pool = ""

    with Spinner(f"Creating '{name}' engine... (this may take several minutes)", f"Engine '{name}' created!"):
        try:
            provider.create_engine(name, size, pool)
        except Exception as e:
            rich.print(f"\n\n[yellow]Error creating engine: {e}")
            divider()
            exit(1)
    divider()

#--------------------------------------------------
# Engine delete
#--------------------------------------------------

@cli.command(name="engines:delete", help="Delete an engine")
@click.option("--name", help="Name of the engine")
def engines_delete(name):
    divider(flush=True)
    ensure_config()
    if not name:
        with Spinner("Fetching engines"):
            try:
                engines = get_resource_provider().list_engines()
            except Exception as e:
                rich.print(f"\n\n[yellow]Error fetching engines: {e}")
                exit(1)
        if len(engines) == 0:
            rich.print("[yellow]No engines found")
            divider()
            sys.exit(0)
        name = controls.fuzzy("Select an engine:", [engine["name"] for engine in engines])
        print("")

    with Spinner(f"Deleting '{name}' engine", f"Engine '{name}' deleted!"):
        try:
            get_resource_provider().delete_engine(name)
        except Exception as e:
            rich.print(f"\n\n[yellow]Error deleting engine: {e}")
    divider()

#--------------------------------------------------
# Import Source flows
#--------------------------------------------------

def import_source_flow(provider: ResourceProvider) -> Sequence[ImportSource]:
    match provider:
        case snowflake.Resources():
            return snowflake_import_source_flow(provider)
        case azure.Resources():
            return azure_import_source_flow(provider)
        case _:
            raise Exception(f"No import source flow available for {type(provider).__module__}.{type(provider).__name__}")

def snowflake_import_source_flow(provider: snowflake.Resources) -> Sequence[ImportSource]:
    with Spinner("Fetching databases", "Databases fetched"):
        try:
            dbs = provider.list_databases()
        except Exception as e:
            rich.print(f"\n\n[yellow]Error fetching databases: {e}")
            dbs = []
    if len(dbs) == 0:
        rich.print("[yellow]No databases found")
        exit(1)
    rich.print()
    db = controls.fuzzy("Select a database:", [db["name"] for db in dbs])
    rich.print()

    with Spinner("Fetching schemas", "Schemas fetched"):
        try:
            schemas = provider.list_sf_schemas(db)
        except Exception as e:
            rich.print(f"\n\n[yellow]Error fetching schemas: {e}")
            schemas = []
    if len(schemas) == 0:
        rich.print("[yellow]No schemas found")
        exit(1)
    rich.print()
    schema = controls.fuzzy("Select a schema:", [s["name"] for s in schemas])
    rich.print()

    with Spinner("Fetching tables", "Tables fetched"):
        try:
            tables = provider.list_tables(db, schema)
        except Exception as e:
            rich.print(f"\n\n[yellow]Error fetching tables: {e}")
            tables = []
    if len(tables) == 0:
        rich.print("[yellow]No tables found")
        exit(1)
    rich.print()
    if tables:
        tables = controls.fuzzy("Select tables (tab for multiple):", [t["name"] for t in tables], multiselect=True)
    else:
        rich.print("[yellow]No tables found")
        tables = ""
    rich.print()
    if isinstance(tables, list):
        return [ImportSourceTable(db, schema, table) for table in tables]
    else:
        return [ImportSourceTable(db, schema, tables)]

def azure_import_source_flow(provider: azure.Resources) -> Sequence[ImportSource]:
    result = controls.file("Select a file:", allow_freeform=True)
    return [ImportSourceFile(result)] if result else []

def import_source_options_flow(provider: ResourceProvider, source: ImportSource, default_options:dict) -> dict:
    match source:
        case ImportSourceFile():
            type: LoadType = default_options.get("type", None)
            if type is None or type == "auto":
                type = Loader.get_type_for(source)
            match type:
                case "csv":
                    return import_source_csv_options_flow(provider, source, default_options)
                case _:
                    pass
        case _:
            pass

    return default_options

def import_source_csv_options_flow(provider: ResourceProvider, source: ImportSourceFile, default_options:dict) -> dict:
    user_specified_schema = {k.strip(): rel_schema_to_type(v.lower()) for k, v in default_options.get("schema", {}).items()}
    user_specified_syntax = default_options.get("syntax", {})

    if source.is_url():
        # @FIXME: Should maybe prompt user to provide a schema manually for urls?
        return {**default_options, "schema": user_specified_schema}

    # Syntax inference + confirmation for local files ==========================

    syntax = CSVLoader.guess_syntax(source.raw_path)
    syntax.update(user_specified_syntax)

    syntax_table = Table(show_header=True, border_style="dim", header_style="bold", box=rich_box.SIMPLE_HEAD)
    for k in syntax.keys():
        syntax_table.add_column(k)
    syntax_table.add_row(*[
        repr(v)[1:-1] if isinstance(v, str) else
        "[dim]<default>[/dim]" if v is None else
        str(v)
        for v in syntax.values()])

    rich.print(syntax_table)

    if not controls.confirm(f"Use this dialect for {source.name}:", True):
        fail_import_options_flow(
            source,
            "You can manually specify the CSV dialectusing syntax arguments. For example, to set the [cyan]delimiter[/cyan] to [green]tab[/green], run:",
            'syntax:[cyan]delim[/cyan]="[green]\\t[/green]"'
        )

    # Schema inference + confirmation for local files ==========================

    schema, csv_chunk = CSVLoader.guess_schema(source.raw_path, syntax)
    schema.update(user_specified_schema)

    schema_table = Table(show_header=True, border_style="dim", header_style="bold", box=rich_box.SIMPLE_HEAD)
    schema_table.add_column("Field")
    schema_table.add_column("Type")
    schema_table.add_column("Ex.")
    for field, type in schema.items():
        schema_table.add_row(field, type.name, f"[dim]{csv_chunk[field][0]}")

    rich.print(schema_table)

    if not controls.confirm(f"Use this schema for {source.name}:", True):
        field = next(iter(schema.keys()))
        fail_import_options_flow(
            source,
            f"You can manually specify column types using schema arguments. For example, to load the column [cyan]{field}[/cyan] as a [green]string[/green], run:",
            f"schema:[cyan]{field}[/cyan]=[green]string[/green]"
        )

    return {**default_options, "schema": schema, "syntax": syntax}

def fail_import_options_flow(source: ImportSourceFile, message: str, solution_args: str):
    prev_cmd_args = " ".join(shlex.quote(arg) for arg in sys.argv[1:])
    saved_args = []
    if "--source" not in sys.argv:
        saved_args.append(f"--source {shlex.quote(source.raw_path)}")
    if "--name" not in sys.argv:
        saved_args.append(f"--name {shlex.quote(source.name)}")

    saved_args = " " + " ".join(saved_args) if saved_args else ""
    print()
    rich.print(message)
    print()
    rich.get_console().print(f"[dim]    rai {prev_cmd_args}{saved_args}[/dim] {solution_args}", highlight=False)
    divider()
    sys.exit(0)


def parse_source(provider: ResourceProvider, raw: str) -> Sequence[ImportSource]:
    if provider.platform == "azure":
        return [ImportSourceFile(raw)]
    elif provider.platform == "snowflake":
        parts = raw.split(".")
        assert len(parts) == 3, "Snowflake table imports must be in `database.schema.table` format"
        return [ImportSourceTable(*parts)]
    else:
        raise Exception(f"Unsupported platform: {provider.platform}")

#--------------------------------------------------
# Imports list
#--------------------------------------------------

@cli.command(name="imports:list", help="List objects imported into RAI")
@click.option("--model", help="Model")
def imports_list(model):
    divider(flush=True)
    ensure_config()
    provider = get_resource_provider()

    if not model:
        with Spinner("Fetching models", "Models fetched"):
            try:
                models = [model["name"] for model in provider.list_graphs()]
            except Exception as e:
                rich.print(f"\n\n[yellow]Error fetching models: {e}")
                exit(1)
        if len(models) == 0:
            rich.print("[yellow]No models found")
            exit(1)
        rich.print()
        model = controls.fuzzy("Select a model:", models)
        rich.print()

    with Spinner(f"Fetching imports for {model}", "Imports fetched"):
        try:
            imports = provider.list_imports(model)
        except Exception as e:
            rich.print(f"\n\n[yellow]Error fetching imports: {e}")
            imports = []

    rich.print()
    if len(imports):
        table = Table(show_header=True, border_style="dim", header_style="bold", box=rich_box.SIMPLE_HEAD)
        cols = {"Import": "name"}
        if len(imports) and "type" in imports[0]:
            cols["Type"] = "type"
        if len(imports) and "id" in imports[0]:
            cols["ID"] = "id"
        if len(imports) and "status" in imports[0]:
            cols["Status"] = "status"

        for label in cols.keys():
            table.add_column(label)

        for imp in imports:
            table.add_row(*[imp.get(attr, None) for attr in cols.values()])
        rich.print(table)
    else:
        rich.print("[yellow]No imports found")

    divider()

#--------------------------------------------------
# Imports stream
#--------------------------------------------------

@supports_platform("snowflake")
@cli.command(name="imports:stream", help="Stream an object into RAI")
@click.option("--source", help="Source")
@click.option("--model", help="Model")
@click.option("--rate", help="Rate")
@click.argument('options', nargs=-1, type=ImportOptionsType())
def imports_stream(source, model, rate, options):
    divider(flush=True)
    ensure_config()
    provider = get_resource_provider()
    default_options = ImportOptionsType.reduce(options)

    if not model:
        with Spinner("Fetching models", "Models fetched"):
            try:
                models = [model["name"] for model in provider.list_graphs()]
            except Exception as e:
                rich.print(f"\n\n[yellow]Error fetching models: {e}")
                exit(1)
        if len(models) == 0:
            rich.print("[yellow]No models found")
            exit(1)
        rich.print()
        model = controls.fuzzy("Select a model:", models)
        rich.print()

    sources = parse_source(provider, source) if source else import_source_flow(provider)
    for import_source in sources:
        try:
            options = import_source_options_flow(provider, import_source, default_options)
            with Spinner(f"Creating stream for {import_source.name}", f"Stream for {import_source.name} created"):
                provider.create_import_stream(import_source, model, rate, options=options)
        except UnsupportedTypeError as err:
            rich.print(f"\n\n[yellow]The [bold]{provider.platform}[/bold] integration doesn't support streaming from [bold]'{err.type}'[/bold] sources.")
        except Exception as e:
            rich.print(f"\n[yellow]Error creating stream: {e}")

    divider()

#--------------------------------------------------
# Imports snapshot
#--------------------------------------------------

@supports_platform("azure")
@cli.command(name="imports:snapshot", help="Load an object once into RAI")
@click.option("--source", help="Source")
@click.option("--model", help="Model")
@click.option("--name", help="Import name")
@click.option("--type", help="Import as type", default="auto", type=click.Choice(["auto", *Loader.type_to_loader.keys()]))
@click.argument('options', nargs=-1, type=ImportOptionsType())
def imports_snapshot(source:str|None, model:str|None, name:str|None, type:str|None, options):
    divider(flush=True)
    ensure_config()
    provider = get_resource_provider()
    default_options = ImportOptionsType.reduce(options)
    default_options["type"] = type

    if not model:
        with Spinner("Fetching models", "Models fetched"):
            try:
                models = [model["name"] for model in provider.list_graphs()]
            except Exception as e:
                rich.print(f"\n\n[yellow]Error fetching models: {e}")
                exit(1)
        if len(models) == 0:
            rich.print("[yellow]No models found")
            exit(1)
        rich.print()
        model = controls.fuzzy("Select a model:", models)
        rich.print()

    sources = parse_source(provider, source) if source else import_source_flow(provider)
    for import_source in sources:
        try:
            import_source.name = name if name else controls.text("name:", import_source.name)
            options = import_source_options_flow(provider, import_source, default_options)
            with Spinner(f"Creating snapshot for {import_source.name}", f"Snapshot for {import_source.name} created"):
                provider.create_import_snapshot(import_source, model, options=options)
        except UnsupportedTypeError as err:
            rich.print(f"\n\n[yellow]The [bold]{provider.platform}[/bold] integration doesn't support loading [bold]'{err.type}'[/bold] files.")
        except RelQueryError as e:
            rich.print(f"\n\n[yellow]Error creating snapshot: {e.pprint()}")
        except Exception as e:
            rich.print(f"\n\n[yellow]Error creating snapshot: {e}")


    divider()

#--------------------------------------------------
# Imports delete
#--------------------------------------------------

@cli.command(name="imports:delete", help="Delete an import from RAI")
@click.option("--object", help="Object")
@click.option("--model", help="Model")
def imports_delete(object, model):
    divider(flush=True)
    ensure_config()
    provider = cast(snowflake.Resources, get_resource_provider())

    if not model:
        with Spinner("Fetching models", "Models fetched"):
            try:
                models = [model["name"] for model in provider.list_graphs()]
            except Exception as e:
                rich.print(f"\n\n[yellow]Error fetching models: {e}")
                exit(1)
        if len(models) == 0:
            rich.print("[yellow]No models found")
            exit(1)
        rich.print()
        model = controls.fuzzy("Select a model:", models)
        rich.print()

    with Spinner(f"Fetching imports for {model}", "Imports fetched"):
        try:
            imports = provider.list_imports(model)
        except Exception as e:
            rich.print(f"\n\n[yellow]Error fetching imports: {e}")
            exit(1)

    if not imports:
        rich.print()
        rich.print("[yellow]No imports to delete")
    if object:
        objects = [object]
    else:
        if len(imports) == 0:
            rich.print("[yellow]No imports found")
            exit(1)
        rich.print()
        objects = controls.fuzzy("Select objects (tab for multiple):", [t["name"] for t in imports], multiselect=True)
        rich.print()

    for object in objects:
        with Spinner(f"Removing {object}", f"{object} removed"):
            try:
                provider.delete_import(object, model)
            except Exception as e:
                rich.print(f"\n\n[yellow]Error deleting import: {e}")

    divider()

#--------------------------------------------------
# Exports list
#--------------------------------------------------

@supports_platform("snowflake")
@cli.command(name="exports:list", help="List objects exported out of RAI")
@click.option("--model", help="Model")
def exports_list(model):
    divider(flush=True)
    ensure_config()
    provider = cast(snowflake.Resources, get_resource_provider())
    coming_soon()

    if not model:
        with Spinner("Fetching models", "Models fetched"):
            try:
                models = [model["name"] for model in provider.list_graphs()]
            except Exception as e:
                rich.print(f"\n\n[yellow]Error fetching models: {e}")
                exit(1)
        if len(models) == 0:
            rich.print("[yellow]No models found")
            exit(1)
        rich.print()
        model = controls.fuzzy("Select a model:", models)
        rich.print()

    with Spinner(f"Fetching exports for {model}", "Exports fetched"):
        try:
            exports = provider.list_exports(model, "")
        except Exception as e:
            rich.print(f"\n\n[yellow]Error fetching exports: {e}")
            exit(1)

    rich.print()
    if len(exports):
        table = Table(show_header=True, border_style="dim", header_style="bold", box=rich_box.SIMPLE_HEAD)
        table.add_column("Object")
        for imp in exports:
            table.add_row(imp.get("name"))
        rich.print(table)
    else:
        rich.print("[yellow]No exports found")

    divider()

#--------------------------------------------------
# Exports delete
#--------------------------------------------------

@supports_platform("snowflake")
@cli.command(name="exports:delete", help="Delete an export from RAI")
@click.option("--export", help="export")
@click.option("--model", help="Model")
def exports_delete(export, model):
    divider(flush=True)
    ensure_config()
    provider = cast(snowflake.Resources, get_resource_provider())
    coming_soon()

    if not model:
        with Spinner("Fetching models", "Models fetched"):
            try:
                models = [model["name"] for model in provider.list_graphs()]
            except Exception as e:
                rich.print(f"\n\n[yellow]Error fetching models: {e}")
                exit(1)
        if len(models) == 0:
            rich.print("[yellow]No models found")
            exit(1)
        rich.print()
        model = controls.fuzzy("Select a model:", models)
        rich.print()

    # @FIXME It seems like we should just fuzzy list exports but this was the original behavior
    source_names = [export] if export else [source.name for source in import_source_flow(provider)]
    for source_name in source_names:
        with Spinner(f"Removing {source_name}", f"{source_name} removed"):
            try:
                provider.delete_export(model, "", source_name)
            except Exception as e:
                rich.print(f"\n\n[yellow]Error deleting export: {e}")

    divider()

#--------------------------------------------------
# Transactions list
#--------------------------------------------------

def nice_duration(millis):
    seconds = millis / 1000
    minutes = seconds / 60
    hours = minutes / 60
    days = hours / 24

    display_days = int(days)
    display_hours = int(hours % 24)
    display_minutes = int(minutes % 60)
    display_seconds = seconds % 60

    parts = []
    if display_days > 0:
        parts.append(f"{display_days}d")
    if display_hours > 0:
        parts.append(f"{display_hours}h")
    if display_minutes > 0:
        parts.append(f"{display_minutes}m")
    if display_seconds > 0:
        parts.append(f"{display_seconds:,.1f}s")
    return " ".join(parts[:3])

def show_transactions(transactions, limit, all_users):
    config = ensure_config()
    if len(transactions):
        table = Table(show_header=True, border_style="dim", header_style="bold", box=rich_box.SIMPLE_HEAD)
        table.add_column("ID")
        table.add_column("Schema")
        table.add_column("State")
        table.add_column("Created")
        table.add_column("Duration", justify="right")

        added = 0
        for txn in transactions:
            if not all_users and txn.get("created_by").lower() != config.get("user", "").lower():
                continue
            if added >= limit:
                break

            match txn.get("state", "").lower():
                case "aborted":
                    style = "red"
                case "completed":
                    style = "white"
                case "created":
                    style = "bold yellow"
                case _:
                    style = ""

            duration = txn.get("duration")
            if duration is None:
                created_on = txn["created_on"]
                duration = (datetime.datetime.now(created_on.tzinfo) - created_on).total_seconds() * 1000

            table.add_row(
                txn.get("id"),
                txn.get("database"),
                txn.get("state"),
                txn.get("created_on").strftime("%Y-%m-%d %H:%M:%S"),
                nice_duration(duration),
                style=style
            )
            added += 1
        rich.print(table)
    else:
        rich.print("[yellow]No transactions found")


@supports_platform("snowflake")
@cli.command(name="transactions:list", help="List transactions")
@click.option("--limit", default=20, help="Limit")
@click.option("--all-users", is_flag=True, help="Show transactions from all users")
def transactions_list(limit, all_users):
    divider()
    ensure_config()
    provider = get_resource_provider()
    with Spinner("Fetching transactions", "Transactions fetched"):
        try:
            transactions = provider.list_transactions(max(limit, 100))
        except Exception as e:
            rich.print(f"\n\n[yellow]Error fetching transactions: {e}")
            exit(1)

    rich.print()
    show_transactions(transactions, limit, all_users)

    divider()

#--------------------------------------------------
# Transaction cancel
#--------------------------------------------------

@supports_platform("snowflake")
@cli.command(name="transactions:cancel", help="Cancel a transaction")
@click.option("--id", help="Transaction ID")
@click.option("--all-users", is_flag=True, help="Show transactions from all users")
def transactions_cancel(id, all_users):
    divider()
    ensure_config()
    provider = get_resource_provider()
    if id is None:
        with Spinner("Fetching transactions", "Transactions fetched"):
            try:
                transactions = provider.list_transactions(20, only_active=True)
            except Exception as e:
                rich.print(f"\n\n[yellow]Error fetching transactions: {e}")
                exit(0)

        if not transactions:
            rich.print("[yellow]No transactions running")
            exit(1)

        show_transactions(transactions, 20, all_users)

        id = controls.fuzzy("Select a transaction to cancel:", [t["id"] for t in transactions])
        print()

    with Spinner("Cancelling transaction", "Transaction cancelled"):
        try:
            provider.cancel_transaction(id)
        except Exception as e:
            rich.print(f"\n\n[yellow]Error cancelling transaction: {e}")

    divider()

#--------------------------------------------------
# Main
#--------------------------------------------------

if __name__ == "__main__":
    # app = EventApp()
    # app.run()
    cli()
