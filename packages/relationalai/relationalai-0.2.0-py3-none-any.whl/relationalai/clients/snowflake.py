# pyright: reportUnusedExpression=false
from collections import defaultdict
import json
import textwrap
from railib.api import TransactionAsyncResponse, poll_with_specified_overhead, _parse_metadata_proto
import requests
import snowflake.connector
import pyarrow as pa
import pandas as pd
import time

from .. import debugging

from typing import Any, Dict, Iterable, Tuple, List, cast
import base64

from pandas import DataFrame

from relationalai.clients.azure import MILLISECONDS_PER_DAY, UNIXEPOCH

from ..tools.cli_controls import Spinner

from ..clients.types import AvailableModel, Import, ImportSource, ImportSourceTable
from ..clients.config import Config
from ..clients.client import Client, ResourceProvider
from .. import dsl, rel, metamodel as m
from ..errors import Errors, RAIException
from .. import std
import re

USE_EXEC_ASYNC = True

#--------------------------------------------------
# Helpers
#--------------------------------------------------

def type_to_sql(type) -> str:
    if type is str:
        return "VARCHAR"
    if type is int:
        return "NUMBER"
    if type is float:
        return "FLOAT"
    if type is bool:
        return "BOOLEAN"
    if type is dict:
        return "VARIANT"
    if type is list:
        return "ARRAY"
    if type is bytes:
        return "BINARY"
    if isinstance(type, dsl.Type):
        return "NUMBER"
    raise ValueError(f"Unknown type {type}")

def type_to_snowpark(type) -> str:
    if type is str:
        return "StringType"
    if type is int:
        return "IntegerType"
    if type is float:
        return "FloatType"
    if type is bool:
        return "BooleanType"
    if type is dict:
        return "MapType"
    if type is list:
        return "ArrayType"
    if type is bytes:
        return "BinaryType"
    if isinstance(type, dsl.Type):
        return "IntegerType"
    raise ValueError(f"Unknown type {type}")

#--------------------------------------------------
# Resources
#--------------------------------------------------

APP_NAME = "___RAI_APP___"

class Resources(ResourceProvider):
    def __init__(self, profile:str|None=None, config:Config|None=None):
        super().__init__(profile, config=config)
        self._conn = None
        self._app_name = "relationalai"
        self._pending_transactions: list[str] = []

    def _exec(self, code:str, params:List[Any]|None = None):
        if not self._conn:
            self._conn = snowflake.connector.connect(
                user=self.config.get('user'),
                password=self.config.get('password'),
                account=self.config.get('account'),
                warehouse=self.config.get('warehouse', ""),
                # database=self.config.get('database', ""),
                # schema=self.config.get('schema', ""),
                role=self.config.get('role', ""),
                client_store_temporary_credential=True,
                client_request_mfa_token=True,
            )
            self._app_name = self.config.get('rai_app_name', "relationalai")
        try:
            return self._conn.cursor().execute(code.replace(APP_NAME, self._app_name), params)
        except Exception as e:
            orig_message = str(e).lower()
            rai_app = self.config.get("rai_app_name", "")
            if re.search(f"database '{rai_app}' does not exist or not authorized.".lower(), orig_message):
                print("\n")
                Errors.snowflake_app_missing(rai_app)
            elif re.search(r"JavaScript execution error", orig_message):
                match = re.search(r"\"message\":\"(.*)\"", orig_message)
                if match:
                    message = match.group(1)
                    if "engine was deleted" in message or "engine not found" in message:
                        Errors.engine_not_found(self.config.get('engine', "Unknown"), message)
                    else:
                        raise RAIException(message) from None
            raise e


    def reset(self):
        self._conn = None

    #--------------------------------------------------
    # Engines
    #--------------------------------------------------

    def list_engines(self):
        results = self._exec(f"select NAME, SIZE, STATUS from {APP_NAME}.api.engines")
        if not results:
            return []
        return [{"name":name, "size":size, "state":state}
                for (name, size, state) in results.fetchall()]

    def get_engine(self, name:str):
        results = self._exec(f"select NAME, SIZE, STATUS from {APP_NAME}.api.engines WHERE NAME='{name}'")
        if not results:
            return None
        return [{"name":name, "size":size, "state":state}
                for (name, size, state) in results.fetchall()][0]

    def create_engine(self, name:str, size:str, pool:str = ""):
        if not pool:
            raise ValueError("Pool is required")
        try:
            self._exec(f"call {APP_NAME}.api.create_engine('{name}', '{pool}', '{size}');")
        except Exception as e:
            raise Exception("Failed to create engine") from e

    def delete_engine(self, name:str):
        self._exec(f"call {APP_NAME}.api.delete_engine('{name}');")

    def suspend_engine(self, name:str):
        raise Exception("Not implemented")

    def resume_engine(self, name:str):
        raise Exception("Not implemented")

    #--------------------------------------------------
    # Graphs
    #--------------------------------------------------

    def list_graphs(self) -> List[AvailableModel]:
        results = self._exec(f"select NAME from {APP_NAME}.api.databases WHERE state <> 'DELETED'")
        if not results:
            return []
        return [{"name": name} for (name,) in results.fetchall()]

    def get_graph(self, name:str):
        results = self._exec(f"""
            select ID, NAME, CREATED_ON, DELETED_ON, STATE
            from {APP_NAME}.api.databases
            where name='{name}' AND state <> 'DELETED'
        """)
        if not results:
            return None
        return results.fetchone()

    def create_graph(self, name: str):
        self._exec(f"call {APP_NAME}.api.create_database('{name}');")

    def delete_graph(self, name:str):
        self._exec(f"call {APP_NAME}.api.delete_database('{name}');")

    #--------------------------------------------------
    # Models
    #--------------------------------------------------

    def list_models(self, database: str, engine: str):
        pass

    def create_models(self, database: str, engine: str, models:List[Tuple[str, str]]) -> List[Any]:
        lines = []
        for (name, code) in models:
            name = name.replace("\"", "\\\"")
            assert "\"\"\"\"\"\"\"" not in code, "Code literals must use fewer than 7 quotes."

            lines.append(textwrap.dedent(f"""
            def delete:rel:catalog:model["{name}"] = rel:catalog:model["{name}"]
            def insert:rel:catalog:model["{name}"] = raw\"\"\"\"\"\"\"{code}\"\"\"\"\"\"\"
            """))
        rel_code = "\n\n".join(lines)
        self.exec_raw(database, engine, rel_code, readonly=False)
        # TODO: handle SPCS errors once they're figured out
        return []

    def delete_model(self, database:str, engine:str, name:str):
        self.exec_raw(database, engine, f"def delete:rel:catalog:model[\"{name}\"] = rel:catalog:model[\"{name}\"]", readonly=False)

    #--------------------------------------------------
    # Exports
    #--------------------------------------------------

    def list_exports(self, database: str, engine: str):
        return []

    def create_export(self, database: str, engine: str, func_name: str, inputs: List[Tuple[str, str, Any]], out_fields: List[Tuple[str, Any]], code: str):
        sql_inputs = ", ".join([f"{name} {type_to_sql(type)}" for (name, var, type) in inputs])
        sql_out = ", ".join([f"{name} {type_to_sql(type)}" for (name, type) in out_fields])
        py_outs = ", ".join([f"StructField(\"{name}\", {type_to_snowpark(type)}())" for (name, type) in out_fields])
        py_inputs = ", ".join([name for (name, *rest) in inputs])
        safe_rel = code.replace("'", "\\'").replace("{", "{{").replace("}", "}}").strip()
        for (name, var, type) in inputs:
            if type is str:
                safe_rel = safe_rel.replace(var, f"'{{{name}.replace(\"'\", \"\\'\")}}'")
            else:
                safe_rel = safe_rel.replace(var, f"{{{name}}}")
        safe_rel = safe_rel.replace("\n", "\\n")
        if py_inputs:
            py_inputs = f", {py_inputs}"
        sql_code = textwrap.dedent(f"""
                CREATE OR REPLACE PROCEDURE {func_name}({sql_inputs})
                RETURNS TABLE({sql_out})
                LANGUAGE PYTHON
                RUNTIME_VERSION = '3.8'
                PACKAGES = ('snowflake-snowpark-python')
                HANDLER = 'handle'
                AS
                $$
                import json
                from snowflake.snowpark import DataFrame
                from snowflake.snowpark.functions import col
                from snowflake.snowpark.types import StringType, IntegerType, StructField, StructType, FloatType, MapType, ArrayType, BooleanType, BinaryType

                def handle(session{py_inputs}):
                    rel_code = f"{safe_rel}"
                    results = session.sql(f"select {APP_NAME}.api.exec('{database}','{engine}','{{rel_code}}', true);")
                    table_results = []
                    for row in results.collect():
                        parsed = json.loads(row[0])
                        table_results.extend(parsed["data"])

                    schema = StructType([{py_outs}])
                    return session.create_dataframe(table_results, schema=schema)
                $$;""")
        start = time.perf_counter()
        self._exec(sql_code)
        debugging.time("export", time.perf_counter() - start, DataFrame(), code=sql_code)
        return

    def delete_export(self, model: str, engine: str, export: str):
        pass

    #--------------------------------------------------
    # Imports
    #--------------------------------------------------

    def list_imports(self, model:str) -> list[Import]:
        # this is roughly copied from the native app code because we don't have a way to
        # get the status of multiple streams at once and doing them individually is way
        # too slow
        results = self._exec(f"""
        select FQ_OBJECT_NAME, nextBatch.status, nextBatch.pending_batches_count,
            from {APP_NAME}.api.data_streams as ds
            left JOIN (
            select
                data_stream_id,
                min_by(status, unloaded) as status,
                min_by(batch_details, unloaded) as batch_details,
                min(unloaded) as unloaded,
                count(*) as pending_batches_count
            from {APP_NAME}.api.data_stream_batches
            where status !in ('loaded')
            group by data_stream_id
            ) nextBatch
            ON ds.id = nextBatch.data_stream_id
            where RAI_DATABASE='{model}';
        """)
        items = []
        if results:
            for stream in results.fetchall():
                (name, status, pending_batches_count) = stream
                if not status and not pending_batches_count:
                    status = "SYNCED"
                if pending_batches_count:
                    status = "SYNCING"
                items.append(cast(Import, {"name": name, "type": "Snowflake object", "status": status}))
        return items

    def create_import_stream(self, source:ImportSource, model:str, rate = 1, options: dict|None = None):
        assert isinstance(source, ImportSourceTable), "Snowflake integration only supports loading from SF Tables right now. Try loading your data as a table via the snowflake interface first."
        object = source.fqn

        if object.lower() in [x["name"].lower() for x in self.list_imports(model)]:
            return

        try:
            self._exec(f"call {APP_NAME}.api.setup_cdc('{self.config.get('engine')}');")
        except Exception:
           pass

        info = self._exec(f"SHOW OBJECTS like %s in {source.database}.{source.schema}", [source.table])
        if not info:
            raise ValueError(f"Object {source.table} not found in {source.database}.{source.schema}")
        else:
            # (time, name, db_name, schema_name, kind, *rest)
            kind = info.fetchone()[4]

        try:
            self._exec(f"ALTER {kind} {object} SET CHANGE_TRACKING = TRUE;")
        except Exception:
            pass

        command = f"""call {APP_NAME}.api.create_data_stream(
            {APP_NAME}.api.object_reference('{kind}', '{object}'),
            '{model}',
            '{object.replace('.', '_').lower()}');"""
        try:
            self._exec(command)
        except Exception as e:
            if "ensure that CHANGE_TRACKING is enabled on the source object" in str(e):
                print("\n")
                Errors.snowflake_change_tracking_not_enabled(object, f"ALTER TABLE {object} SET CHANGE_TRACKING = TRUE;")
            raise e

        return

    def create_import_snapshot(self, source:ImportSource, model:str, _: dict|None = None):
        raise Exception("Snowflake integration doesn't support snapshot imports yet")

    def delete_import(self, import_name:str, model:str):
        self._exec(f"""call {APP_NAME}.api.delete_data_stream(
             '{import_name}',
             '{model}'
        );""")
        return

    #--------------------------------------------------
    # Exec Sync
    #--------------------------------------------------

    def _exec_sync_raw(self, database:str, engine:str, raw_code:str, readonly=True, inputs = {}):
        if inputs:
            raise Exception("Inputs aren't currently supported using exec_sync in SPCS.")

        return self._exec(f"select {APP_NAME}.api.exec('{database}','{engine}','{raw_code}', {readonly});")

    def _format_results_sync(self, results, task:m.Task) -> Tuple[DataFrame, List[Any]]:
        parsed_results = []
        parsed_problems = []
        if results:
            for row in results:
                parsed = json.loads(row[0])
                if parsed.get("problems"):
                    for problem in parsed["problems"]:
                        parsed_problems.append(problem)
                else:
                    parsed_results.extend(parsed["data"])
        try:
            data_frame = DataFrame(parsed_results, columns=task.return_cols())
        except Exception:
            data_frame = DataFrame(parsed_results)
        return (data_frame, parsed_problems)

    #--------------------------------------------------
    # Exec Async
    #--------------------------------------------------

    def _check_exec_async_status(self, txn_id: str):
        """Check whether the given transaction has completed."""
        response = self._exec(f"CALL {APP_NAME}.api.get_transaction('{txn_id}');")
        assert response, f"No results from get_transaction('{txn_id}')"
        status: str = next(iter(response))[2]

        if status == "ABORTED":
            raise Exception(f"Transaction aborted while waiting for results '{txn_id}'")

        return status == "COMPLETED"

    def _list_exec_async_artifacts(self, txn_id: str) -> Dict[str, str]:
        """Grab the list of artifacts produced in the transaction and the URLs to retrieve their contents."""
        response = self._exec(f"CALL {APP_NAME}.api.list_transaction_outputs('{txn_id}');")
        assert response, f"No results from list_transaction_outputs('{txn_id}')"
        return {name: url for name, url in response}

    def _fetch_exec_async_artifacts(self, artifact_urls: Dict[str, str]) -> Dict[str, Any]:
        """Grab the contents of the given artifacts from SF."""
        contents = {}
        with requests.Session() as session:
            for name, url in artifact_urls.items():
                response = session.get(url)
                response.raise_for_status() # throw if something goes wrong.
                if name.endswith(".json"):
                    contents[name] = response.json()
                else:
                    contents[name] = response.content

        return contents

    def _parse_exec_async_results(self, arrow_files: List[Tuple[str, bytes]]):
        """Mimics the logic in _parse_arrow_results of railib/api.py#L303 without requiring a wrapping multipart form."""
        results = []

        for file_name, file_content in arrow_files:
            with pa.ipc.open_stream(file_content) as reader:
                schema = reader.schema
                batches = [batch for batch in reader]
                table = pa.Table.from_batches(batches=batches, schema=schema)
                results.append({"relationId": file_name, "table": table})

        return results

    def _exec_async_raw(self, database:str, engine:str, raw_code:str, readonly=True, inputs={}):
        if inputs:
            raise Exception("Inputs aren't currently supported using exec_async in SPCS.")

        response = self._exec(f"CALL {APP_NAME}.api.exec_async('{database}','{engine}','{raw_code}', {readonly});")
        if not response:
            raise Exception("No results from exec_async")

        # Grab the txn_id from the response
        txn_id, status = next(iter(response))
        debugging.event("transaction", txn_id=txn_id)
        # Wait for completion or failure
        if status != "COMPLETED":
            self._pending_transactions.append(txn_id)
            poll_with_specified_overhead(lambda: self._check_exec_async_status(txn_id), 0.2)

        self._pending_transactions.remove(txn_id)

        # List the result artifacts (and the URLs to retrieve them)
        artifact_urls = self._list_exec_async_artifacts(txn_id)
        # Actually retrieve them
        artifacts = self._fetch_exec_async_artifacts(artifact_urls)

        meta = _parse_metadata_proto(artifacts["metadata.proto"])
        meta_json = artifacts["metadata.json"]

        # We use the metadata to map arrow files to the relations they contain data for.
        # In Azure, this is provided sideband via response headers.
        arrow_files_to_relations = {}
        for ix, relation in enumerate(cast(Any, meta).relations):

            arrow_file = relation.file_name
            relation_id = meta_json[ix]["relationId"]
            arrow_files_to_relations[arrow_file] = relation_id

        # Hydrate the arrow files into tables
        results = self._parse_exec_async_results([(arrow_files_to_relations[name], content) for name, content in artifacts.items() if name.endswith(".arrow")])

        rsp = TransactionAsyncResponse()
        # @FIXME: Hardcoding the `state` feels somewhat unsafe, but we can't have gotten here in the code otherwise.
        # @FIXME: Missing `response_format_version`, which isn't obviously present anywhere in the results.
        rsp.transaction = {"id": txn_id, "state": "COMPLETED", "response_format_version": None}
        rsp.metadata = meta
        rsp.problems = artifacts["problems.json"]
        rsp.results = results
        return rsp

    # Copied directly from azure.py
    def _has_errors(self, results):
        if len(results.problems):
            for problem in results.problems:
                if problem['is_error'] or problem['is_exception']:
                    return True

    # Copied directly from azure.py
    def _format_results_async(self, results, task:m.Task) -> Tuple[DataFrame, List[Any]]:
        data_frame = DataFrame()
        if len(results.results):
            for result in results.results:
                types = [t for t in result["relationId"].split("/") if t != "" and not t.startswith(":")]
                result_frame:DataFrame = result["table"].to_pandas()
                for i, col in enumerate(result_frame.columns):
                    if "UInt128" in types[i]:
                        result_frame[col] = result_frame[col].apply(lambda x: base64.b64encode(x.tobytes()).decode()[:-2])
                    if types[i] == "Dates.DateTime":
                        result_frame[col] = pd.to_datetime(result_frame[col] - UNIXEPOCH, unit="ms")
                    if types[i] == "Dates.Date":
                        result_frame[col] = pd.to_datetime(result_frame[col] * MILLISECONDS_PER_DAY - UNIXEPOCH, unit="ms")
                ret_cols = task.return_cols()
                if len(ret_cols) and len(result_frame.columns) == len(ret_cols):
                    result_frame.columns = task.return_cols()[0:len(result_frame.columns)]
                result["table"] = result_frame
                if ":output" in result["relationId"]:
                    data_frame = pd.concat([data_frame, result_frame], ignore_index=True)
        return (data_frame, results.problems)

    #--------------------------------------------------
    # Exec
    #--------------------------------------------------

    def exec_raw(self, database:str, engine:str, raw_code:str, readonly=True, inputs: dict = {}):
        raw_code = raw_code.replace("'", "\\'") # @NOTE: If collapsing to a single exec, make sure to copy this line into it.
        if USE_EXEC_ASYNC:
            return self._exec_async_raw(database, engine, raw_code, readonly, inputs=inputs)
        else:
            return self._exec_sync_raw(database, engine, raw_code, readonly, inputs=inputs)

    def format_results(self, results, task:m.Task) -> Tuple[DataFrame, List[Any]]:
        if USE_EXEC_ASYNC:
            return self._format_results_async(results, task)
        else:
            return self._format_results_sync(results, task)

    #--------------------------------------------------
    # Transactions
    #--------------------------------------------------

    def list_transactions(self, limit:int, only_active=False):
        where = "WHERE state <> 'COMPLETED'" if only_active else ""
        field_names = [
            "id", "database_name", "state", "abort_reason", "read_only", "created_by",
            "duration", "created_on", "finished_at"
        ]
        sql_fields = ", ".join([f.upper() for f in field_names])
        results = self._exec(f"select {sql_fields} from {APP_NAME}.api.transactions {where} LIMIT %s", [limit])
        if not results:
            return []
        map = {"database_name": "database"}
        mapped = [map.get(f, f) for f in field_names]
        return [dict(zip(mapped, row)) for row in results.fetchall()]

    def cancel_transaction(self, transaction_id):
        self._exec(f"CALL {APP_NAME}.api.CANCEL_TRANSACTION(%s);", [transaction_id])
        if transaction_id in self._pending_transactions:
            self._pending_transactions.remove(transaction_id)

    def cancel_pending_transactions(self):
        for txn_id in self._pending_transactions:
            self.cancel_transaction(txn_id)

    #--------------------------------------------------
    # Snowflake specific
    #--------------------------------------------------

    def get_version(self):
        results = self._exec(f"SELECT {APP_NAME}.app.get_release()")
        if not results:
            return None
        return results.fetchone()[0]

    def list_warehouses(self):
        results = self._exec("SHOW WAREHOUSES")
        if not results:
            return []
        return [{"name":name}
                for (name, *rest) in results.fetchall()]

    def list_compute_pools(self):
        results = self._exec("SHOW COMPUTE POOLS")
        if not results:
            return []
        return [{"name":name}
                for (name, *rest) in results.fetchall()]

    def list_roles(self):
        results = self._exec("SELECT CURRENT_AVAILABLE_ROLES()")
        if not results:
            return []
        # the response is a single row with a single column containing
        # a stringified JSON array of role names:
        row = results.fetchone()
        if not row:
            return []
        return [{"name": name} for name in json.loads(row[0])]

    def list_apps(self):
        results = self._exec("SHOW APPLICATIONS")
        if not results:
            return []
        return [{"name":name}
                for (time, name, *rest) in results.fetchall()]

    def list_databases(self):
        results = self._exec("SHOW DATABASES")
        if not results:
            return []
        return [{"name":name}
                for (time, name, *rest) in results.fetchall()]

    def list_sf_schemas(self, database:str):
        results = self._exec(f"SHOW SCHEMAS IN {database}")
        if not results:
            return []
        return [{"name":name}
                for (time, name, *rest) in results.fetchall()]

    def list_tables(self, database:str, schema:str):
        results = self._exec(f"SHOW OBJECTS IN {database}.{schema}")
        items = []
        if results:
            for (time, name, db_name, schema_name, kind, *rest) in results.fetchall():
                items.append({"name":name, "kind":kind.lower()})
        return items

    def schema_info(self, database:str, schema:str, tables:Iterable[str]):
        pks = self._exec(f"SHOW PRIMARY KEYS IN SCHEMA {database}.{schema};")
        fks = self._exec(f"SHOW IMPORTED KEYS IN SCHEMA {database}.{schema};")
        tables = ", ".join([f"'{x.upper()}'" for x in tables])
        columns = self._exec(f"""
            select TABLE_NAME, COLUMN_NAME, DATA_TYPE
            from {database.upper()}.INFORMATION_SCHEMA.COLUMNS
            where TABLE_SCHEMA = '{schema.upper()}'
            and TABLE_NAME in ({tables})
            and TABLE_CATALOG = '{database.upper()}';
        """)
        results = defaultdict(lambda: {"pks": [], "fks": {}, "columns": {}})
        if pks:
            for row in pks:
                results[row[3].lower()]["pks"].append(row[4].lower()) # type: ignore
        if fks:
            for row in fks:
                results[row[7].lower()]["fks"][row[8].lower()] = row[3].lower()
        if columns:
            for row in columns:
                results[row[0].lower()]["columns"][row[1].lower()] = row[2].lower()
        return results

#--------------------------------------------------
# Snowflake Wrapper
#--------------------------------------------------

class PrimaryKey:
    pass

class Snowflake:
    def __init__(self, model, auto_import=False):
        self._model = model
        self._auto_import = auto_import
        if not isinstance(model._client.resources, Resources):
            raise ValueError("Snowflake model must be used with a snowflake config")
        self._dbs = {}
        imports = model._client.resources.list_imports(model.name)
        self._import_structure(imports)

    def _import_structure(self, imports: list[Import]):
        tree = self._dbs
        # pre-create existing imports
        schemas = set()
        for item in imports:
            database_name, schema_name, table_name = item["name"].lower().split('.')
            database = getattr(self, database_name)
            schema = getattr(database, schema_name)
            schemas.add(schema)
            schema._add(table_name, is_imported=True)
        for schema in schemas:
            schema._finalize()
        return tree

    def __getattribute__(self, __name: str) -> 'SnowflakeDB':
        if __name.startswith("_"):
            return super().__getattribute__(__name)
        __name = __name.lower()
        if __name in self._dbs:
            return self._dbs[__name]
        self._dbs[__name] = SnowflakeDB(self, __name)
        return self._dbs[__name]

class SnowflakeDB:
    def __init__(self, parent, name):
        self._name = name
        self._parent = parent
        self._model = parent._model
        self._schemas = {}

    def __getattribute__(self, __name: str) -> 'SnowflakeSchema':
        if __name.startswith("_"):
            return super().__getattribute__(__name)
        __name = __name.lower()
        if __name in self._schemas:
            return self._schemas[__name]
        self._schemas[__name] = SnowflakeSchema(self, __name)
        return self._schemas[__name]

class SnowflakeSchema:
    def __init__(self, parent, name):
        self._name = name
        self._parent = parent
        self._model = parent._model
        self._tables = {}

    def _finalize(self):
        self._table_info = self._model._client.resources.schema_info(self._parent._name, self._name, self._tables.keys())
        for table in self._tables.values():
            table._finalize()

    def _add(self, name, is_imported=False):
        name = name.lower()
        if name in self._tables:
            return self._tables[name]
        self._tables[name] = SnowflakeTable(self, name, is_imported=is_imported)
        return self._tables[name]

    def __getattribute__(self, __name: str) -> 'SnowflakeTable':
        if __name.startswith("_"):
            return super().__getattribute__(__name)
        return self._add(__name)

class SnowflakeTable(dsl.Type):
    def __init__(self, parent, name, is_imported=False):
        super().__init__(parent._model, f"sf_{name}", ["namespace", "fqname", "describe"])
        self._name = name
        self._model = parent._model
        self._parent = parent
        self._aliases = {}
        self._finalzed = False
        if not is_imported and self._parent._parent._parent._auto_import:
            with Spinner(f"Creating stream for {self.fqname()}", f"Stream created for {self.fqname()}"):
                db_name = parent._parent._name
                schema_name = parent._name
                self._model._client.resources.create_import_stream(ImportSourceTable(db_name, schema_name, name), self._model.name)
            print("")
            parent._tables[name] = self
            parent._finalize()
        elif not is_imported:
            Errors.snowflake_import_missing(debugging.capture_code_info(4), self.fqname(), self._model.name)


    def _finalize(self):
        if self._finalzed:
            return

        self._finalzed = True
        self._schema = self._parent._table_info[self._name]
        relation_name = self.fqname().replace(".", "_").lower()
        model:dsl.Graph = self._model
        model.install_raw(f"bound {relation_name}")

        with model.rule(dynamic=True):
            prop, id, val = std.Vars(3)
            if self._schema["pks"]:
                getattr(getattr(std.rel, relation_name), self._schema["pks"][0].upper())(id, val)
            else:
                getattr(std.rel, relation_name)(prop, id, val)
            self.add(snowflake_id=id)

        for prop, prop_type in self._schema["columns"].items():
            with model.rule():
                id, val = std.Vars(2)
                getattr(getattr(std.rel, relation_name), prop.upper())(id, val)
                self(snowflake_id=id).set(**{prop.lower(): val})

    def namespace(self):
        return f"{self._parent._parent._name}.{self._parent._name}"

    def fqname(self):
        return f"{self.namespace()}.{self._name}"

    def describe(self, **kwargs):
        model = self._model
        for k, v in kwargs.items():
            if v is PrimaryKey:
                self._schema["pks"] = [k]
            elif isinstance(v, tuple):
                (table, name) = v
                if isinstance(table, SnowflakeTable):
                    fk_table = table
                    pk = fk_table._schema["pks"]
                    with model.rule():
                        inst = fk_table()
                        me = self()
                        getattr(inst, pk[0]) == getattr(me, k)
                        me.set(**{name: inst})
                else:
                    raise ValueError(f"Invalid foreign key {v}")
            else:
                raise ValueError(f"Invalid column {k}={v}")
        return self

#--------------------------------------------------
# Graph
#--------------------------------------------------

def Graph(name, *, profile:str|None=None, config:Config, dry_run:bool=False):
    client = Client(Resources(profile, config), rel.Compiler(config), name, dry_run=dry_run)
    client.install("pyrel_base", dsl.build.raw_task("""
        @inline
        def make_identity(x..., z) =
            hash128({x...}, x..., u) and
            hash_value_uint128_convert(u, z)
            from u

        @inline
        def pyrel_default[F, c](k..., v) =
            F(k..., v) or (not F(k..., _) and v = c)
    """))
    return dsl.Graph(client, name)
