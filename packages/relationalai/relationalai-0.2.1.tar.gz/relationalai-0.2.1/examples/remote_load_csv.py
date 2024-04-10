import relationalai as rai

model = rai.Model("Test")

Person = model.Type("Person")
Criminal = model.Type("Criminal")

# loaded from `examples/data/people.csv`
with model.read("people.csv") as row:
    # id,name,age,account,criminal
    # P-00007333,Tommy Roman,18,,False

    person = Person.add(id=row.id).set(name=row.name, age=row.age)
    with row.account:
        person.set(account=row.account)
    with row.criminal:
        person.set(Criminal)

with model.query() as select:
    p = Person()
    res = select(p.id, p.name, p.age)

print(res.results)
