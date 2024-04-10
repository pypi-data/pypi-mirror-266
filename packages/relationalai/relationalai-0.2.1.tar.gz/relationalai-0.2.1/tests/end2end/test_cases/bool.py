#pyright: reportUnusedExpression=false
import relationalai as rai

model = rai.Model("test_bool", config=globals().get("test_config"))
Person = model.Type("Person")
Adult = model.Type("Adult")

with model.rule():
    Person.add(name="Joe", age=74)
    Person.add(name="Bob", age=40)
    Person.add(name="Jane", age=10)

with model.rule():
    p = Person()
    p.age >= 18
    p.set(Adult, cool=False)

with model.rule():
    p = Person()
    p.age < 18
    p.set(cool=True)

with model.query() as select:
    a = Adult()
    a.cool == False # noqa
    z = select(a, a.name, a.age)

print(z.results)

with model.query() as select:
    p = Person(cool=True)
    z = select(p, p.name)

print(z.results)
