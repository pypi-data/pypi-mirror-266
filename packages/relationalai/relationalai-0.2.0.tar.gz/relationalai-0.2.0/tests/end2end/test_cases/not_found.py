import relationalai as rai

model = rai.Model("TestNotFound", config=globals().get("test_config"))
Invited = model.Type("Invited")
Invite = model.Type("Invite")
Person = model.Type("Person")

with model.rule():
    joe = Person.add(name="Joe", age=74)
    bob = Person.add(name="Bob", age=40)
    jane = Person.add(name="Jane", age=10)

    joe.set(friend=jane).set(friend=bob)
    jane.set(friend=joe)
    bob.set(friend=jane)

    Invited.add(person=joe)

with model.rule():
    p = Person()
    with model.not_found():
        Invited(person=p)

    Invite.add(person=p)

with model.query() as select:
    p = Person()
    p.friend.age > 10
    with model.not_found():
        p.friend.name == "Joe"
    res = select(p, p.name, p.age, p.friend.name, p.friend.age)

with model.query() as select:
    res = select(Invite().person.name)
