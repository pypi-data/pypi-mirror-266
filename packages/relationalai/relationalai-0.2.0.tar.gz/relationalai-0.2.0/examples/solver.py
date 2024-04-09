#pyright: reportUnusedExpression=false
import rich
import relationalai as rai
from relationalai.std import rel as r, Vars

#--------------------------------------------------
# Helpers
#--------------------------------------------------

def pprint(title, res):
    rich.print("[dim]\n--------------------------------------------------")
    rich.print(f"\n[green]{title}")
    rich.print("")
    if isinstance(res, rai.dsl.ContextSelect):
        rich.print(res.results)
    rich.print(res)

#--------------------------------------------------
# Load a directory of Rel
#--------------------------------------------------

model = rai.Model("MyCoolModel")
model.load_raw("rel/")

#--------------------------------------------------
# Do a query with some of our loaded relations
#--------------------------------------------------

with model.query() as select:
    a,b = Vars(2)
    r.foo(a, b)
    r.bar(a + 5)
    z = select(a, b)

pprint("Foo/Bar results", z)

#--------------------------------------------------
# Execute a raw string of rel
#--------------------------------------------------

res = model.exec_raw("""
    def model2 = rel_primitive_solverapi_model[
        :min, vars,  obj[vars:x, vars:y], cons[vars:x, vars:y]
    ]
    def solved2 = rel:solverapi:solve[model2, "HiGHS", {}]
    def extracted2 = rel:solverapi:extract[model2, solved2]
    def sol2 = extracted2:point
    def output = extracted2:termination_status, sol2:x, sol2:y
""", raw_results=False)

pprint("Exec raw results", res)

#--------------------------------------------------
# Query the solver relations
#--------------------------------------------------

with model.query() as select:
    sol = r.sol
    info = select(r.extracted.termination_status(), sol.x(), sol.y())

pprint("Solver results", info)

#--------------------------------------------------
# Read a relation from solver.rel
#--------------------------------------------------

with model.query() as select:
    status, x, y, obj = Vars(4)
    r.info(status, x, y, obj)
    info = select(status, x, y, obj)

pprint("Solver info", info)

#--------------------------------------------------
# Load some data
#--------------------------------------------------

# Person = model.Type("Person")
# with model.rule():
#     Person.add(name="Joe", age=74)
#     Person.add(name="Bob", age=40)
#     Person.add(name="Jane", age=10)
