#pyright: reportUnusedExpression=false
import relationalai as rai

model = rai.Model("test_collections", config=globals().get("test_config"))
model._config.set("compiler.use_multi_valued", True)

Person = model.Type("Person")
Adult = model.Type("Adult")

Person.foos.has_many()

with model.rule():
    p = Person.add(name="Joe", age=74)
    p.foos.extend([8,9,0])
    Person.add(name="Bob", age=40)
    Person.add(name="Jane", age=10)

with model.rule():
    p = Person()
    foos = p.foos
    p.age >= 18
    foos.extend([1,2,3])
    p.age.in_([10,20,40,74])
    p.set(Adult)

# This rule makes sure that we aren't incorrectly removing the get
# for a collection if we do an append on the same property instance
with model.rule():
    p = Person()
    foos = p.foos
    foos > 8
    foos.add(11)

with model.query() as select:
    p = Person()
    p.foos.in_([8,9,0])
    z = select(p.name)

print(z.results)

with model.query() as select:
    p = Person()
    z = select(p.name, p.foos)

print(z.results)

with model.query() as select:
    p = Person(name="Joe")
    a, b, c = p.foos.choose(3)
    z = select(p.name, a, b, c)

print(z.results)

with model.query() as select:
    p = Person()
    p2 = Person()
    p < p2
    p.foos == p2.foos
    z = select(p.name, p2.name)

print(z.results)

with model.query() as select:
    a = Adult()
    z = select(a, a.name, a.age)

print(z.results)

model._config.set("compiler.use_multi_valued", False)