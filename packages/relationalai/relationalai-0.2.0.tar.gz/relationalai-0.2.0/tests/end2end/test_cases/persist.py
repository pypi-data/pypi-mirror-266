#pyright: reportUnusedExpression=false
import relationalai as rai

model = rai.Model("test_persist", config=globals().get("test_config"))
Person = model.Type("Person")
Adult = model.Type("Adult")
PersistFoo = model.Type("PersistFoo")

with model.query():
    PersistFoo.persist(p_name="Foo2")
    PersistFoo.persist(p_name="Foo3")

with model.query() as select:
    p = PersistFoo()
    z = select(p, p.p_name)

print("Persists!\n")
print(z.results)

with model.query():
    p = PersistFoo()
    p.unpersist(p_name=p.p_name)

with model.query() as select:
    p = PersistFoo()
    z = select(p, p.p_name)

print("\nUnpersists!\n")
print(z.results)