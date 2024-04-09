import os
from typing import Dict, Any, cast
from railib import config
import configparser
import toml
import tomlkit
from tomlkit.items import Table


#--------------------------------------------------
# config defaults
#--------------------------------------------------

FIELD_PLACEHOLDER = ""

snowflake_default_props = {
    "platform": "snowflake",
    "user": FIELD_PLACEHOLDER,
    "password": FIELD_PLACEHOLDER,
    "account": FIELD_PLACEHOLDER,
    "role": "PUBLIC",
    "warehouse": FIELD_PLACEHOLDER,
    "rai_app_name": FIELD_PLACEHOLDER,
    "engine": FIELD_PLACEHOLDER,
}

azure_default_props = {
    "platform": "azure",
    "host": "azure.relationalai.com",
    "port": 443,
    "region": "us-east",
    "scheme": "https",
    "client_credentials_url": "https://login.relationalai.com/oauth/token",
    "client_id": FIELD_PLACEHOLDER,
    "client_secret": FIELD_PLACEHOLDER,
}

all_prop_keys = set(snowflake_default_props.keys()) | set(azure_default_props.keys())

_no_default = object()

#--------------------------------------------------
# helpers
#--------------------------------------------------

class ConfigFile:
    def __init__(
        self,
        path: str | None = None,
        cfg: Dict[str, Any] = {},
        *,
        format = "toml"
    ):
        if format == "toml":
            self.path:str|None = path
            self.profiles:Dict[str,Dict[str,Any]] = cfg.get("profile", {})
            self.config:Dict[str,Any] = {}
            for key in cfg:
                if key != "profile":
                    self.config[key] = cfg[key]
        elif format == "ini":
            self.path = path
            self.profiles = {
                k: {k2: v2 for k2, v2 in v.items()}
                for k, v in cfg.items()
                if k != "DEFAULT"
            }
            self.config = {}
        else:
            raise ValueError(f"Unsupported format: {format}")

    def apply_keymap(self):
        keymap = {
            "active-profile": "active_profile",
            "snowflake-connection": "snowflake_connection",
            "snowsql_user": "user",
            "snowsql_pwd": "password",
        }
        new_config = {}
        for key in self.config:
            new_config[keymap.get(key, key)] = self.config[key]
        self.config = new_config
        new_profiles = {}
        for profile, props in self.profiles.copy().items():
            new_profiles[profile] = {}
            for key in props.copy():
                # self.profiles[profile][keymap.get(key, key)] = props[key]
                new_profiles[profile][keymap.get(key, key)] = props[key]
        self.profiles = new_profiles

    def get_combined_profiles(self):
        combined_profiles = {}
        combined_profiles["__top_level__"] = self.config or {}
        for profile in self.profiles:
            combined_profiles[profile] = self.profiles[profile].copy()
        return combined_profiles

    def map(self, f):
        """
        Apply a function `f` to all props dictionaries in the configuration files, including the top-level dictionary and all profiles.
        """
        combined_profiles = self.get_combined_profiles()
        for profile in combined_profiles:
            combined_profiles[profile] = f(combined_profiles[profile])
        config = combined_profiles.pop("__top_level__")
        return self.__class__(
            self.path, { **config, "profile": combined_profiles }
        )

    def filled_from_snowflake_connection(self):
        def fill(props):
            if "snowflake_connection" in props:
                connection_name = props.pop("snowflake_connection")
                snowflake_config = get_from_snowflake_connections_toml()
                if snowflake_config and connection_name in snowflake_config:
                    return {
                        **snowflake_config[connection_name],
                        **props,
                    }
            return props
        return self.map(fill)

    def merge(self, other):
        """
        Merge the profiles from `other` into this ConfigFile object
        """
        combined_profiles = self.get_combined_profiles()
        other_combined_profiles = other.get_combined_profiles()

        all_profile_names = set(combined_profiles) | set(other_combined_profiles)

        for profile in all_profile_names:
            self_profile = combined_profiles.get(profile, {})
            other_profile = other_combined_profiles.get(profile, {})
            combined_profiles[profile] = {**other_profile, **self_profile}

        config = combined_profiles.pop("__top_level__", None)

        if config is not None:
            self.config = config
        self.profiles = combined_profiles


def first(x):
    return next(iter(x), None)

def _search_upwards_for_file(file:str):
    """
    Search for `file` in the current directory and all parent directories.

    Returns the absolute path to the file if found, otherwise None.
    """
    dir = os.path.abspath(os.getcwd())
    while True:
        file_path = os.path.join(dir, file)
        if os.path.isfile(file_path):
            yield file_path
        parent_dir = os.path.dirname(dir)
        if parent_dir == dir:
            break # reached the root
        dir = parent_dir

def _search_userdir_for_file(file:str):
    """
    Search for `file` in the user's home directory.

    Returns the absolute path to the file if found, otherwise None.
    """
    file_path = os.path.expanduser(f"~/{file}")
    if os.path.isfile(file_path):
        yield file_path

def _find_config_file():
    yield from _search_upwards_for_file("raiconfig.toml")
    yield from _search_userdir_for_file(".rai/raiconfig.toml")

def _parse_and_map_config(file:str):
    """
    Parse the config file at `file` and return a dictionary of config values.

    Handles both TOML and INI files.
    """
    if not os.path.exists(file):
        return ConfigFile(cfg={})
    if file.endswith(".toml"):
        try:
            cf = ConfigFile(file, toml.load(file))
            cf.apply_keymap()
            return cf
        except toml.TomlDecodeError as e:
            raise Exception(f"Error parsing {file}: {e}")
    config = configparser.ConfigParser()
    config.read(file)
    cf = ConfigFile(file, {k: v for k, v in config.items() if k != "DEFAULT"}, format="ini")
    cf.apply_keymap()
    return cf

def _get_full_config(profile:str|None=None) -> tuple[Dict[str,Any], str|None]:
    """
    Returns a dictionary representing the props to be used for the currently active profile. Incorporates the following rules:
    1. The `snowflake_connection` key fills in the properties from the Snowflake connections.toml file.
    2. Profiles with the same name are merged in order of appearance, with earlier profiles taking precedence.
    3. The profile indicated by the `active_profile` key is merged into other top-level properties.
    """
    files = list(_find_config_file())
    file_path = first(files)
    if not files:
        return {}, file_path
    config_files = [
        _parse_and_map_config(file).filled_from_snowflake_connection()
        for file in files
    ]
    for i in range(len(config_files) - 1, 0, -1):
        config_files[i-1].merge(config_files[i])
    if not config_files:
        return {}, file_path
    root_file = config_files[0]
    if profile:
        root_file.config["active_profile"] = profile
    if ("active_profile" in root_file.config and
        root_file.config["active_profile"] in root_file.profiles):
        active_profile = root_file.config["active_profile"]
        config = {
            **root_file.profiles[active_profile],
            **root_file.config,
        }
    else:
        config = root_file.config
    return config, file_path

def has_platform(cfg, platform):
    return any(profile.get("platform") == platform for profile in cfg.get_combined_profiles().values())

def _legacy_config_files():
    """
    Generates all legacy config files found

    Includes both ~/.rai/config and rai.config (in a parent directory
    or the user's home directory)
    """
    yield from _search_upwards_for_file("rai.config")
    yield from _search_userdir_for_file(".rai.config")
    path = os.path.expanduser("~/.rai/config")
    if os.path.exists(path):
        yield path

def legacy_config_exists():
    return any(_legacy_config_files())

def all_configs_including_legacy():
    for file in _find_config_file():
        yield _parse_and_map_config(file)
    for file in _legacy_config_files():
        yield _parse_and_map_config(file)

def get_from_snowflake_connections_toml():
    user_config_path = os.path.expanduser("~/.snowflake/connections.toml")
    if os.path.exists(user_config_path):
        try:
            snow_config = toml.load(user_config_path)
        except toml.TomlDecodeError as e:
            raise Exception(f"Error parsing {user_config_path}: {e}")
        config = {}
        for profile in snow_config:
            config[profile] = {}
            for key in snow_config[profile]:
                config[profile][key] = snow_config[profile][key]
        return config

def to_rai_config(data:Dict[str, Any]) -> Dict[str, Any]:
    creds = config._read_client_credentials(data)
    _keys = ["host", "port", "region", "scheme", "audience"]
    result = {k: v for k, v in data.items() if k in _keys}
    result["credentials"] = creds
    return result


#--------------------------------------------------
# Config
#--------------------------------------------------

class Config():
    def __init__(self, profile:str|Dict[str,Any]|None=None, fetch=True):
        supplied_props = None
        if isinstance(profile, dict):
            supplied_props = profile
            profile = "__top_level__"
        if fetch:
            self.fetch(profile)
        else:
            self.profile = "__top_level__"
            self.props = {}
        self.cache_config_file_contents()
        if supplied_props is not None:
            for k, v in supplied_props.items():
                self.set(k, v)
            if not self.file_path:
                self.file_path = "__inline__"

    def get_profiles(self):
        if not self.original_toml:
            return {}
        return self.original_toml.get("profile", {})

    def fetch(self, profile:str|None=None):
        profile = profile or os.environ.get("RAI_PROFILE", None)
        cfg, path = _get_full_config(profile)
        self.profile = profile or cfg.get("active_profile", "__top_level__")
        self.file_path = path
        self.props = cfg

    def cache_config_file_contents(self):
        self.original_toml = tomlkit.document()
        if os.path.exists("raiconfig.toml"):
            with open("raiconfig.toml", "r") as f:
                try:
                    content = f.read()
                    if not content.endswith("\n"):
                        content += "\n"
                    self.original_toml = tomlkit.parse(content)
                except toml.TomlDecodeError as e:
                    raise Exception(f"Error parsing {self.file_path}: {e}")
            return

    def clone_profile(self):
        self.props = {k: v for k,v in self.props.items()}

    def get(self, name:str, default:Any=_no_default, strict:bool=True):
        parts = name.split(".")
        props = self.props

        for part in parts[:-1]:
            props = props.get(part)
            if props is None:
                props = {}
                break

        val = props.get(parts[-1], os.environ.get(name, default))
        if val is _no_default and strict:
            raise Exception(f"Missing config value for '{name}'")
        if val is _no_default:
            val = None
        return val

    def set(self, name:str, value:str|int):
        parts = name.split(".")
        props = self.props
        for part in parts[:-1]:
            if part not in props:
                props[part] = {}
            props = props[part]
        props[parts[-1]] = value

    def clear_props(self):
        self.props = {}

    def unset(self, name:str):
        del self.props[name]

    def update(self, other, save_progress=False):
        self.props.update(other)

    def __contains__(self, key):
        return key in self.props

    def items(self):
        return self.props.items()

    def print(self):
        for k, v in self.items():
            print(f"{k}: {v}")

    def to_rai_config(self) -> Dict[str, Any]:
        return to_rai_config(self.props)

    def save(self):
        new_document = tomlkit.document()

        # handle the active_profile key that appears at the top:
        if self.profile != "__top_level__":
            active_profile = self.profile
        else:
            active_profile = self.get("active_profile", None)
        if active_profile is not None:
            new_document["active_profile"] = active_profile

        # add key-value pairs at the top level if this is the top-level profile:
        if self.profile == "__top_level__":
            for k, v in self.props.items():
                if k != "active_profile":
                    new_document[k] = v

        active_profile_table = tomlkit.table()
        for k, v in self.props.items():
            active_profile_table[k] = v

        original_top_level_profile = None

        profiles = tomlkit.table(is_super_table=True)

        def adjust_trailing_newlines(item, action):
            match item.__class__.__name__:
                case "TOMLDocument":
                    body = getattr(item, "body", None)
                    if body is None or len(body) == 0:
                        return
                    adjust_trailing_newlines(body[-1], action)
                case "tuple":
                    if len(item) < 2:
                        return
                    _, value = item
                    adjust_trailing_newlines(value, action)
                case "Container":
                    body = getattr(item, "body", None)
                    if body is None or len(body) == 0:
                        return
                    adjust_trailing_newlines(body[-1], action)
                case "Table":
                    value = getattr(item, "value", None)
                    if value is None:
                        return
                    adjust_trailing_newlines(value, action)
                case "Whitespace":
                    action(item)

        def ensure_profiles_added():
            if not new_document.get("profile"):
                # this hack is necessary because tomlkit sometimes
                # inserts spurious newlines just before the profile
                # section
                # related: https://github.com/sdispater/tomlkit/issues/48
                def trim_one(item):
                    if item.value.endswith("\n"):
                        item._s = item.value[:-1]
                adjust_trailing_newlines(new_document, trim_one)
                new_document.add("profile", profiles)

        # fill in from the original TOML file contents:
        for key, value in self.original_toml.items():
            # the "active-profile" check is here to make the migration smooth
            # from when we used "active-profile" instead of "active_profile"
            if key == "profile":
                ensure_profiles_added()
                for profile in value:
                    if profile == active_profile:
                        profiles.add(profile, active_profile_table)
                    else:
                        profiles.add(profile, value[profile])
            if key in new_document or key == "active_profile":
                continue
            elif key in all_prop_keys:
                ensure_profiles_added()
                if not original_top_level_profile:
                    k = 0
                    while True:
                        original = "original" if k == 0 else f"original-{k}"
                        if self.original_toml.get("profile", {}).get(original) is None:
                            break
                        k += 1
                    original_top_level_profile = original
                    profiles.add(original_top_level_profile, tomlkit.table())
                original_profile = cast(Table, profiles.get(original_top_level_profile))
                original_profile.add(key, value)
            else:
                # preserve all keys unrelated to the profiles:
                new_document[key] = value

        if active_profile is not None:
            ensure_profiles_added()
            if profiles.get(active_profile) is None:
                profiles.add(active_profile, active_profile_table)

        with open("raiconfig.toml", "w") as f:
            f.write(new_document.as_string())

    def _fill_in_with_defaults(self, defaults: Dict[str, Any], **kwargs):
        props = {k: v for k, v in kwargs.items() if k in defaults}
        self.update({
            **defaults,
            **self.props,
            **props,
        }, save_progress=True)

    def fill_in_with_azure_defaults(self, **kwargs):
        self._fill_in_with_defaults(azure_default_props, **kwargs)

    def fill_in_with_snowflake_defaults(self, **kwargs):
        self._fill_in_with_defaults(snowflake_default_props, **kwargs)

    def fill_in_with_defaults(self):
        platform = self.get("platform", None)
        if platform == "azure":
            self.fill_in_with_azure_defaults()
        elif platform == "snowflake":
            self.fill_in_with_snowflake_defaults()
        else:
            self.set("platform", "snowflake")
            self.fill_in_with_snowflake_defaults()