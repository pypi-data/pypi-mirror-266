import os
import shutil
import subprocess

simple_program_body = """
Person = model.Type("Person")

with model.rule():
    alex = Person.add(name="Alex", age=19)
    bob = Person.add(name="Bob", age=47)
    carol = Person.add(name="Carol", age=17)
    deb = Person.add(name="Deb", age=17)

    carol.set(friend=deb)
    alex.set(friend=bob)
    alex.set(friend=carol)

with model.query() as select:
    alex = Person(name="Alex")
    person = alex.friend
    person.age >= 21
    response = select(person.name)

print(response.results)
# Output:
#   name
# 0  Bob
"""

hello_world_pyrel_example = f"""
import relationalai as rai

model = rai.Model("people")

{simple_program_body}
"""

hello_world_expected_output = """
  name
0  Bob
"""

example_with_profile = f"""
import relationalai as rai

model = rai.Model("people", profile="test")

{simple_program_body}
"""

example_with_explicit_config = f"""
import relationalai as rai
from relationalai.clients import config as cfg

config = cfg.Config({{
    "platform": "azure",
    "host": "azure.relationalai.com",
    "port": 443,
    "region": "us-east",
    "scheme": "https",
    "client_credentials_url": "https://login.relationalai.com/oauth/token",
    "client_id": "{os.getenv("RAI_CLIENT_ID")}",
    "client_secret": "{os.getenv("RAI_CLIENT_SECRET")}",
    "engine": "aaa",
}})

model = rai.Model("people", config=config)

{simple_program_body}
"""

def get_project_dir():
    dir = os.path.abspath(__file__)
    for i in range(3):
        dir = os.path.dirname(dir)
    return dir

def setup_tempdir(replace:bool=True):
    tempdir = os.path.expanduser("~/temp-relationalai-test")
    if replace:
      if os.path.exists(tempdir) and os.path.isdir(tempdir):
          shutil.rmtree(tempdir)
      os.mkdir(tempdir)
      os.chdir(tempdir)
    elif not os.path.exists(tempdir):
      os.mkdir(tempdir)
      os.chdir(tempdir)
    if not replace:
       return tempdir

    print("Current working directory:", os.getcwd())
    print("Project directory:", get_project_dir())
    print("Creating a virtual environment...")
    subprocess.run(["python", "-m", "venv", ".venv"], capture_output=True)
    print("Installing relationalai-python...")
    subprocess.run(
        [".venv/bin/python", "-m", "pip", "install", "-e", get_project_dir()],
        capture_output=True,
    )
    return tempdir