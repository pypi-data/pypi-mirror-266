
# RelationalAI Configuration

## Basic

### Using a Configuration File

To configure a new RelationalAI project after setting up a virtual environment and doing `pip install relationalai`, use the `rai init` command from your project's root directory:

```sh
rai init             # if the environment is already activated
.venv/bin/rai init   # if the environment is not activated
```

This command asks you to use which platform you want to use (Snowflake or Azure), and then asks for the necessary credentials to connect to the platform. It writes this information in a file called `raiconfig.toml` in your project root. This configuration information will be used by any Python process running from this directory or any of its subdirectories.

The configuration options, along with default values, are as follows for Snowflake:

```toml
platform = "snowflake"
user = ""
password = ""
account = ""
role = "PUBLIC"
warehouse = ""
database = ""
rai_app_name = ""
engine = ""
```

And for Azure:

```toml
platform = "azure"
host = "azure.relationalai.com"
port = 443
region = "us-east"
scheme = "https"
client_credentials_url = "https://login.relationalai.com/oauth/token"
client_id = ""
client_secret = ""
```

You can add tables to this file to create multiple profiles. The names of those tables should be prefixed with `profile`. Here's an example showing a profile called `field-team`:

```toml
[profile.field-team]
platform = "azure"
host = "azure.relationalai.com"
port = 443
region = "us-east"
scheme = "https"
client_credentials_url = "https://login.relationalai.com/oauth/token"
client_id = ""
client_secret = ""
```

To use specific profile, you can specify the profile name in `rai.Model()` in your, as in `rai.Model(profile="my-other-profile")`. Alternatively, you can assign the `active_profile` key in the `config` table:

```toml
active_profile = "field-team"

[profile.field-team]
platform = "azure"
host = "azure.relationalai.com"
port = 443
region = "us-east"
scheme = "https"
client_credentials_url = "https://login.relationalai.com/oauth/token"
client_id = ""
client_secret = ""
```

### Manual Configuration

If you want to avoid using `raiconfig.toml`, you can manually configure the RelationalAI package by constructing a configuration object in your code. Typically this would be done in conjunction with environment variables, so that you don't have to hard-code your credentials in your code:

```python
import relationalai as rai
from relationalai.clients import config as cfg
import os

config = cfg.Config({
    "platform": "snowflake",
    "user": "my_username",
    "password": os.getenv("SNOWFLAKE_PASSWORD"),
    "account": "my_account",
    "role": "PUBLIC",
    "warehouse": "my_warehouse",
    "database": "my_database",
    "rai_app_name": "my_app_name",
    "engine": "my_engine",
})

model = rai.Model(config=config)
```

### The `RAI_PROFILE` environment variable

If the `RAI_PROFILE` environment variable is set and the `profile` and `config` parameters of `rai.Model` are not supplied, the `relationalai` package will use `RAI_PROFILE` to determine which `raiconfig.toml` profile to use.

## Where do I find my credentials?

The `rai init` command will help you fill in many of the values you need. However, there are a few values you will need to find on your own.

### Snowflake

Your Snowflake `user` and `password` are the same values you use to log in to the Snowflake web interface. To find your account value, log into `https://app.snowflake.com` and then look at the part of the URL after `https://app.snowflake.com` and replace the slash with a dash. For example, if your URL were `https://app.snowflake.com/plvoura/client_solutions`, the value you should use for `account` in your credentials is `plvoura-client_solutions`.

### Azure

To get your `client_id` and `client_secret`, you will need to create an OAuth client in the Console. Visit `https://console.relationalai.com`, log in, and click the Settings icon in the left sidebar. If you don't have a gear-shaped icon there, it means that you don't have the necessary permissions to create an OAuth client. You will need to ask your administrator to create one for you.

On the Settings page, click New OAuth CLient, then select the checkboxes corresponding to the permissions you want to give the OAuth client. For example, you might select the top-level `transaction`, `database`, and `engine` permissions. Then click Save at the bottom of the page. You will see your client ID and secret in the top right corner; you can click the copy icon on each one to copy them to your clipboard.i

## Advanced

### Profiles

If you want to re-use credentials across multiple projects, you can save a `raiconfig.toml` file in the directory `~/.rai`, where `~` is your home directory. Here's an example of what such a file might look like:

```toml
[profile.field-team]
platform = "snowflake"
user = "my_username"
password = "my_password"
account = "my_account"
role = "PUBLIC"
warehouse = "my_warehouse"
database = "my_database"
rai_app_name = "my_app_name"
engine = "my_engine"

[profile.engineering-team]
platform = "Azure"
host = "azure.relationalai.com"
port = 443
region = "us-east"
scheme = "https"
client_credentials_url = "https://login.relationalai.com/oauth/token"
client_id = "my_client_id"
client_secret = "my_client_secret"
```

This file has two *profiles*, namely `field-team` and `engineering-team`.

To use the configuration file from `~/.rai`, you can a save `raiconfig.toml` in your project directory that looks like this:

```toml
active_profile = "field-team"
```

The `relationalai` package will fill in the values from the `field-team` profile in `~/.rai/raiconfig.toml`.

You can also override configuration keys from the parent configuration file by specifying them in the child configuration file. For example, if you wanted to use your `field-team` profile but with a different engine for a particular project, you could use a `raiconfig.toml` file like this:

```toml
active_profile = "field-team"
engine = "special_field_team_engine"
```

### Snowflake connections

If you have a [Snowflake connection file](https://docs.snowflake.com/en/developer-guide/python-connector/python-connector-connect#connecting-using-the-connections-toml-file) at `~/.snowflake/connections.toml`, you can re-use those credentials by using a `snowflake_connection` key. For example, your `~/.snowflake/connections.toml` file might look like this:

```toml
[my-snowflake-connection]
account = "my_account"
user = "my_username"
password = "my_password"
warehouse = "my_warehouse"
database = "my_database"
schema = "my_schema"
role = "PUBLIC"
```

And your `raiconfig.toml` file might look like this:

```toml
snowflake_connection = "my-snowflake-connection"
rai_app_name = "my_app_name"
engine = "my_engine"
```

Notice that the `raiconfig.toml` specifies keys that are not present in the `~/.snowflake/connections.toml` file. If there are any keys in common, the `raiconfig.toml` file takes precedence.