from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, cast
from relationalai.analysis.mechanistic import Mechanism

from pandas import DataFrame
from ..clients.client import Client
from .. import debugging
from .. import dsl, rel, metamodel as m

@dataclass
class Query:
    task: m.Task
    ix: int
    code: str|None = None
    err: Exception|None = None
    result: Any = None
    mech: Mechanism|None = None

    def to_json(self):
        return {
            "task": str(self.task),
            "ix": self.ix,
            "code": self.code,
            "err": str(self.err),
            "mech": self.mech.stack[-1] if self.mech else None
        }


@dataclass
class Install:
    task: m.Task
    name: str|None = None
    code: str|None = None
    err: Exception|None = None
    mech: Mechanism|None = None

    def to_json(self):
        return {
            "task": str(self.task),
            "name": self.name,
            "code": self.code,
            "err": str(self.err),
            "mech": self.mech.stack[-1] if self.mech else None
        }


class Document():
    blocks: list[Query | Install]
    query_count: int

    def __init__(self):
        self.blocks = []
        self.query_count = 0

    def __str__(self):
        parts = []
        h = "==[ Document ]"
        print(f"{h}{'='*(80 - len(h))}")
        for block in self.blocks:
            match block:
                case Query():
                    h = f"----[ Query {block.ix} ]"
                    parts.append(f"{h}{'-'*(80 - len(h))}")
                    parts.append(str(block.task))
                case Install():
                    h = f"----[ Rule {block.name} ]"
                    parts.append(f"{h}{'-'*(80 - len(h))}")
                    parts.append(str(block.task))

        return "\n".join(parts)

class Config():
    def get(self, key:str, default:Any=None):
        return default

class NoopClient():
    def __init__(self, *_args, config=None, **_kwargs):
        self.compiler = rel.Compiler(config or Config())
        self.resources = Resources(config or Config())

    def query(self, task: m.Task, *args, **kwargs):
        self.compiler.compile(task)
        return DataFrame()

    def install(self, name: str, task: m.Task, *args, **kwargs):
        self.compiler.compile(task)

    def export_udf(self, name, inputs, out_fields, task):
        pass

    def exec_raw(self, raw_code:str):
        raise Exception("Cannot exec raw code in test executor")

    def load_raw_file(self, path:str):
        raise Exception("Cannot load raw file in test executor")

proxied_clients: list[Document] = []

class Resources():
    def __init__(self, config:Config):
        self.config = config

def proxy_client(client_class, throw_on_error = True):
    class ProxiedClient(client_class, Document):
        def __init__(self, *args, throw_on_error = True, **kwargs):
            self.blocks: list[Query | Install] = []
            self.query_count = 0
            self.throw_on_error = throw_on_error
            # self.capture_handler = CaptureHandler()

            # debugging.logger.addHandler(self.capture_handler)
            super().__init__(*args, **kwargs)
            proxied_clients.append(self)

        # def __del__(self):
        #     # @FIXME: This is apparently not reliable
        #     debugging.logger.removeHandler(self.capture_handler)

        @contextmanager
        def capture_debugging(self):
            orig_logger_debug = debugging.logger.debug
            msgs = []
            def capture(msg):
                msgs.append(msg)
                orig_logger_debug(msg)

            setattr(debugging.logger, "debug", capture)
            try:
                yield msgs
            finally:
                setattr(debugging.logger, "debug", orig_logger_debug)

        def get_emitted(self, msgs: list):
            msgs[0]["emitted"] if len(msgs) > 0 and msgs[0]["event"] == "compilation" else None

        def query(self, task:m.Task, *args, **kwargs):
            ix = self.query_count
            self.query_count += 1
            res = None
            with self.capture_debugging() as msgs:
                mech = None
                try:
                    mech = Mechanism(task)
                    res = super().query(task, *args, **kwargs)
                    self.blocks.append(Query(task, ix, self.get_emitted(msgs), None, res, mech))

                except Exception as err:
                    self.blocks.append(Query(task, ix, self.get_emitted(msgs), err, None, mech))
                    if self.throw_on_error:
                        raise

            return res

        def install(self, name, task:m.Task, *args, **kwargs):
            with self.capture_debugging() as msgs:
                mech = None
                try:
                    mech = Mechanism(task)
                    super().install(name, task, *args, **kwargs)
                    self.blocks.append(Install(task, name, self.get_emitted(msgs), None, mech))
                except Exception as err:
                    self.blocks.append(Install(task, name, self.get_emitted(msgs), err, mech))
                    if self.throw_on_error:
                        raise

    return ProxiedClient

Executor = proxy_client(NoopClient, throw_on_error=False)

def Graph(name, engine:str|None=None, dry_run=False, config=None):
    client = cast(Client, Executor(name, engine, dry_run, config=config or Config()))
    return dsl.Graph(client, name)
