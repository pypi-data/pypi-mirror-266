from contextlib import contextmanager
import io
import os
from pathlib import Path

import rich
from rich.syntax import Syntax

from relationalai.clients.test import Document, Query
from relationalai import clients, debugging
from gentest.util import PROJECT_DIR
from gentest.validate.roundtrip import exec_and_run_callback

AzureClient = clients.azure.Client
SnowflakeClient = clients.snowflake.Client
AzureProxyClient = clients.test.proxy_client(AzureClient)
SnowflakeProxyClient = clients.test.proxy_client(SnowflakeClient)

@contextmanager
def proxy_clients():
    try:
        clients.azure.Client = AzureProxyClient
        clients.snowflake.Client = SnowflakeProxyClient
        yield
    finally:
        clients.azure.Client = AzureClient
        clients.snowflake.Client = SnowflakeClient


def path_to_slug(path: Path, base_path:str|Path = PROJECT_DIR):
    return str(path.relative_to(base_path)).replace("/", "__").replace(".py", "")

def validate_query_results(file_path: Path, snapshot, ns:dict|None = None):
    with open(file_path, "r") as file:
        code = file.read()
        with proxy_clients():
            # @TODO: Consider suppressing stdout
            doc: Document = exec_and_run_callback(code, None, ns=ns)
            for block in doc.blocks:
                if isinstance(block, Query):
                    try:
                        snapshot.assert_match(str(block.result), f"query{block.ix}.txt")
                    except AssertionError as err:
                        header, info, _, *body = str(err).splitlines()
                        with io.StringIO() as buf:
                            console = rich.console.Console(file=buf, force_terminal=True)
                            console.print(header)
                            console.print(info)

                            source_info = debugging.get_source(block.task)
                            assert source_info and source_info.line is not None
                            source = debugging.find_block_in(code, source_info.line, str(file_path))

                            console.print()
                            base = os.getcwd()
                            console.print("In", f"./{file_path.relative_to(base)}" if file_path.is_relative_to(base) else file_path)
                            if source.source:
                                console.print(Syntax(source.source, "python", dedent=True, line_numbers=True, start_line=source.line, padding=1))

                            console.print('\n'.join(body))
                            raise Exception(buf.getvalue()) from None
