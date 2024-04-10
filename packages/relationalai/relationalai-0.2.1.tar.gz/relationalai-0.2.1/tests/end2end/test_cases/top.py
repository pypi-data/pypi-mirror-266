#pyright: reportUnusedExpression=false
import relationalai as rai
from relationalai.std import aggregates

model = rai.Model("test_top", config=globals()["test_config"])
Person = model.Type("Person")

with model.rule():
    Person.add(name="Joe", age=74)
    Person.add(name="Bob", age=40)
    Person.add(name="Jane", age=15)
    Person.add(name="Alex", age=33)
    Person.add(name="John", age=27)

with model.query() as select:
    p = Person()
    aggregates.top(3, p.age)
    select(p, p.name, p.age)
