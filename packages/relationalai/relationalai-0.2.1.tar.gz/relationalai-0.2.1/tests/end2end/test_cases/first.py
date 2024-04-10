import relationalai as rai

model = rai.Model("FirstSnapshotTest", config=globals()["test_config"])

Person = model.Type("Person")

with model.rule():
    Person.add(name="Sam Watson")
    Person.add(name="Pete Vilter")
    Person.add(name="Josh Cole")

with model.query() as select:
    p = Person()
    select(p.name) # @NOTE: we don't actually need to use the result, it'll get snapshotted all the same
