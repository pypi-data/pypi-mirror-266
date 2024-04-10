#pyright: reportUnusedExpression=false
import relationalai as rai

graph = rai.Model("MyCoolDatabase")
Person = graph.Type("Person")
Adult = graph.Type("Adult")
Child = graph.Type("Woop")

with graph.rule():
    Person.add(name="Joe", age=74)
    Person.add(name="Bob", age=40)
    Person.add(name="Jane", age=10)

with graph.rule():
    p = Person()

with graph.rule():
    p = Person()
    with p.age >= 18:
        p.set(Adult)
    with p.age < 18:
        p.set(Child)

with graph.query() as select:
    # a = Adult();
    a = Person(Adult|Child)
    z = select(a, a.name, a.age)

print("People!\n")
print(z.results)






