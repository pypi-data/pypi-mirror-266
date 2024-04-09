#pyright: reportUnusedExpression=false
import relationalai as rai

model = rai.Model("MyCoolDatabase")
Person = model.Type("Person")
Adult = model.Type("Adult")

with model.rule():
    j=Person.add(name="Joe", age=74)
    b=Person.add(name="Bob", age=20)
    Person.add(name="Jane", age=10, friend=j).set(friend=b)

with model.rule():
    p = Person()
    p.age >= 18
    p.set(Adult)

with model.query() as select:
    a = Person()
    with model.found():
        a.friend.age > a.age + 30
    z = select(a, a.name, a.age, a.friend.name, a.friend.age)

print("People!\n")
print(z.results)