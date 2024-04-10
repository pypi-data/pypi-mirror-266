import pexpect
import subprocess
import os
import shutil
import tomlkit

import time

from common import (
    hello_world_pyrel_example,
    hello_world_expected_output,
    setup_tempdir,
    example_with_profile,
    example_with_explicit_config,
)

down_arrow = "\033[B"
enter = "\r"
delete = "\x7f"

def test_basic_flow():
    tempdir = setup_tempdir()

    fake_home_dir = os.path.join(tempdir, "home")
    env = {
        "HOME": fake_home_dir,
        "TERM": "dumb",
    }

    print("Writing to example.py...")
    with open("example.py", "w") as f:
        f.write(hello_world_pyrel_example)

    print("Writing to example_with_profile.py...")
    with open("example_with_profile.py", "w") as f:
        f.write(example_with_profile)

    print("Writing to example_with_explicit_config.py...")
    with open("example_with_explicit_config.py", "w") as f:
        f.write(example_with_explicit_config)
    
    print("Writing to example_with_profile_reference.py...")
    with open("example_with_profile_reference.py", "w") as f:
        f.write(hello_world_pyrel_example)

    with open("init.log", "wb") as f:
        print("Init flow...")
        os.environ["TERM"] = "dumb"
        client_id = os.getenv("RAI_CLIENT_ID") or ""
        secret = os.getenv("RAI_CLIENT_SECRET") or ""
        if not client_id or not secret:
            raise ValueError(
                "Environment variables `RAI_CLIENT_ID` and `RAI_CLIENT_SECRET` must be set for this test to be properly run."
            )
        child = pexpect.spawn(".venv/bin/rai init", env=env)  # type: ignore
        child.logfile = f
        child.expect(r"Host platform")
        print("Selecting platform...")
        child.send(down_arrow)
        time.sleep(1)
        child.send(enter)
        child.expect(r"Client ID")
        print(f"Entering Client ID... ({client_id[:5]}...)")
        child.sendline(client_id)
        child.expect(r"Client Secret")
        print(f"Entering Client Secret... ({secret[:5]}...)")
        child.sendline(secret)
        print("Waiting for the engine selection list...")
        child.expect(r"Select an engine")
        print("Selecting engine...")
        time.sleep(0.2)
        child.send(down_arrow)
        child.send(enter)
        child.expect(pexpect.EOF)
        child.close()

    for file in [
        "example.py",
        "example_with_profile.py",
        "example_with_explicit_config.py",
        "example_with_profile_reference.py",
    ]:
        if file == "example_with_profile.py":
            # change the name of the table in raiconfig.toml from default to test:
            with open("raiconfig.toml", "r") as f:
                original = tomlkit.load(f)
                table = tomlkit.table()
                for k, v in original.items():
                    table[k] = v
                doc = tomlkit.document()
                doc.add("profile", tomlkit.table())
                doc["profile"].add("test", table) # type: ignore
            with open("raiconfig.toml", "w") as f:
                f.write(doc.as_string())
        if file == "example_with_profile_reference.py":
            # change the name of the table in raiconfig.toml from default to test:
            with open("raiconfig.toml", "r") as f:
                # content = f.read()
                original = tomlkit.load(f)
                doc = tomlkit.document()
                doc["active_profile"] = "test"
                doc.add("profile", tomlkit.table())
                doc["profile"].add("test", original["profile"]["test"]) # type: ignore
            with open("raiconfig.toml", "w") as f:
                f.write(doc.as_string())
        print(f"Running {file}...")
        result = subprocess.run(
            [".venv/bin/python", file], capture_output=True, text=True, env=env
        )
        assert result.stdout.strip() == hello_world_expected_output.strip()

    shutil.rmtree(tempdir)  # Remove the directory and all its contents
