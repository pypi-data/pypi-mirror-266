import time
from hypothesis import Verbosity, given, settings
from gentest.gen.action import gen_task_body
from gentest.gen.scope import GenScope, GenScopeBuilder
from gentest.gen.task import gen_task
from relationalai import metamodel as mm
from gentest.gen import ir
from gentest.gen.context import fixture
from gentest import fixtures



if __name__ == "__main__":
    ctx = fixture(fixtures.person_place_thing).finish()
    print(str(ctx))

    root_builder = GenScopeBuilder(ctx)

    root = root_builder.finish()
    # example_scope = gen_provision_stage(root).example()
    # print(str(example_scope[1]))

    runs = 0

    @settings(max_examples=100, verbosity=Verbosity.quiet)
    # @given(construct_scope(root).flatmap(gen_expr_examples))
    # @given(gen_expr_examples(example_scope))
    @given(gen_task_body(root, 5))
    def show(stuff: tuple[list[ir.Action], GenScope]):
        global runs
        runs += 1
        print("-"*80)
        actions, _ = stuff
        print("    -", "\n    - ".join(str(v) for v in actions))
        # scope, values = stuff
        # for v in values:
        #     if isinstance(v, ir.Call):
        #         break
        # else:
        #     return

        # print(str(scope))
        # print("Values")
        # for v in values:
        #     rich.print(f"    - {str(v)}")

    action_count = 0
    best_score = 0
    best = None

    @settings(max_examples=100, verbosity=Verbosity.quiet)
    @given(gen_task(root))
    def show_task(task: mm.Task):
        global runs, action_count, best_score, best
        runs += 1
        action_count += len(task.items)

        score = len(task.items)
        if score > best_score:
            best_score = score
            best = task

        # print("task", "-"*75)
        # print(str(task))
        # print("="*80)

    start = time.time_ns()
    show_task()
    end = time.time_ns()
    elapsed = (end - start) / 1000000
    print(f"Completed {runs} runs in {elapsed:.2f}ms. Avg { elapsed / runs:.4f}ms per task.")
    print(f"with {action_count} total actions Avg {action_count / runs:.1f} actions per task, { elapsed / action_count:.4f}ms per action in task.")

    print("Ex.")
    print(str(best))
