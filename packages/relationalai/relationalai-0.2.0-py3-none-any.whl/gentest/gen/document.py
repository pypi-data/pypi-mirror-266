from typing import Sequence
from hypothesis import given, settings, strategies as gen
from gentest.emit import DocumentEmitter
from relationalai import metamodel as mm
from relationalai.clients.test import Document, Install, Query
from gentest.gen.scope import GenScope
from gentest.gen.task import gen_task
from gentest import fixtures
from gentest.gen.context import fixture

def gen_query(scope: GenScope):
    return gen_task(scope).map(lambda task: ("query", task)) # @FIXME

def gen_rule(scope: GenScope):
    return gen_task(scope).map(lambda task: ("install", task))

def gen_block(scope: GenScope):
    return gen_rule(scope) | gen_query(scope)

def gen_document(root_scope: GenScope):
    return gen.lists(gen_block(root_scope), min_size=1, max_size=10).map(into_document)


def into_document(blocks: Sequence[tuple[str, mm.Task]]) -> Document:
    doc = Document()
    for (type, task) in blocks:
        match type:
            case "query":
                doc.blocks.append(Query(task, doc.query_count))
                doc.query_count += 1
            case "install":
                doc.blocks.append(Install(task))
            case _:
                raise Exception(f"Unknown block type {type} for task {str(task)}")

    return doc

if __name__ == "__main__":
    ctx = fixture(fixtures.person_place_thing).finish()
    root = GenScope(ctx)

    @settings(max_examples=200)
    @given(gen_document(root))
    def foo(doc: Document):
        print("="*80)
        print("blocks:", len(doc.blocks))
        print(DocumentEmitter.from_document(doc).stringify())
        print("="*80)
    foo()
