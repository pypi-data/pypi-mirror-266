#pyright: reportUnusedExpression=false
from typing import Tuple
import relationalai as rai

# Since exports aren't supported in Azure, we'll do this as a dry run
# to test just the bytecode generation
model = rai.Model("test_export", dry_run=True, config=globals().get("test_config"))
Person = model.Type("Person")
Adult = model.Type("Adult")

with model.rule():
    Person.add(name="Joe", age=74)
    Person.add(name="Bob", age=40)
    Person.add(name="Jane", age=10)

with model.rule():
    p = Person()
    p.age >= 18
    p.set(Adult)

@model.export("sandbox.public")
def test_export() -> Tuple[str, int]:
    a = Adult()
    return a.name, a.age
