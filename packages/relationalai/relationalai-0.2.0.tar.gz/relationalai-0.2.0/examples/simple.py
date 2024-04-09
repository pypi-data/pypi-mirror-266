#pyright: reportUnusedExpression=false
import relationalai as rai

model = rai.Model("MyCoolDatabase")
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

with model.query() as select:
    a = Adult()
    z = select(a, a.name, a.age)

print("People!\n")
print(z.results)







