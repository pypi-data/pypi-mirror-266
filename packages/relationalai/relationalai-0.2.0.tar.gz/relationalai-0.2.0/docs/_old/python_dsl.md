# Python DSL sketch

Rather than create our own language, we could create a Python DSL that allows us to write rules and queries in Python. This lets us leverage the existing Python tooling ecosystem and provides something "familiar" to our users.

## The quickstart

```python
from rai import csv
import rai

graph = rai.Graph()

# Get our node types

Person = graph.Type("Person")
Adult = graph.Type("Adult")
Customer = graph.Type("Customer")
Error = graph.Type("Error")
Suspicious = graph.Type("Suspicious")
ImmediateReview = graph.Type("ImmediateReview")

fraud = rai.snowflake.fraud
Criminal = graph.Type(fraud.Criminal)
Transaction = graph.Type(fraud.Transaction)
ReviewQueue = graph.Type(fraud.ReviewQueue)

# Add some people and a rule to label adults

Person.add(name="Joe", age=30)
Person.add(name="Jane", age=30)

with graph.rule():
    p = Person(); p.age > 18
    p.set(Adult)

# Load and validate people

with graph.rule():
    (name, age, account) = csv.load("people.csv")
    p = Person.ensure(name=name, age=age)
    with account:
        p.set(Customer, account=account)

with graph.rule():
    Customer(Adult=False)
    Error.add(message="Customers must be adults")

# Look for suspicious transactions

with graph.rule():
    t = Transaction(_from=Customer(), to=Criminal())
    t.set(Suspicious)
    with t.amount > 10000:
        t.set(ImmediateReview, review_reason="Large transaction to criminal")

Path = graph.Path
Transfer = graph.Edge(Transaction, Transaction.payer, Transaction.payee)

with graph.rule():
    c, c2 = Criminal(), Criminal()
    path = shortest(Path(c, Transfer[1:2], c2))
    start = path.edges[0]
    start.set(ImmediateReview, path=path, review_reason="Criminal to criminal transaction")

# Write back to the ReviewQueue in snowflake

with graph.rule():
    t = Transaction.get(ImmediateReview)
    ReviewQueue.add(transaction=t, reason=t.review_reason, path=either(t.path, [t]))

```

## Graph query examples

```python

Edge = graph.Edge
Path = graph.Path

# // Find any single unit path between two objects
with graph.query() as select:
    path = Path(Person, Edge, Criminal)
    select(path)

# // Capture what edge is found between two objects
with graph.query() as select:
    path = Path(Person, Edge, Criminal)
    select(path.edges[0])

# // Find people that are connected through a specific set of edges
with graph.query() as select:
    p1, p2 = Person(), Person()
    path = Path(p1, p1.knows | p1.likes, p2)
    select(p1, p2)

# // Capture which edge they are connected through
with graph.query() as select:
    p1, p2 = Person(), Person()
    path = Path(p1, p1.knows | p1.likes, p2)
    select(p1, p2, path.edges[0].name)

# // People connected by knows or friend to a student, teacher, or principle
with graph.query() as select:
    p1, p2 = Person(), Student | Teacher | Principle
    path = Path(p1, p1.knows | p1.likes, p2)
    select(p1, p2, path.edges[0].name)

# // Find a path between a person and a cat/dog that is 1 to 10 edges long
with graph.query() as select:
    path = Path(Person, Edge[1:10], Cat|Dog)
    select(path)

# // Connect through an edge that has properties
with graph.query() as select:
    p, c = Person(), Criminal()
    t1 = Transaction(); t1.amount > 1000
    path = Path(p, t1, c)
    select(p, c)

# // Connect a person through a chain 1 or 2 transactions to a criminal
with graph.query() as select:
    p, c = Person(), Criminal()
    path = Path(p, Transaction[1:2], c)
    select(p, c)

# // Find a chain of 2 to 5 transactions that ends in a criminal
with graph.query() as select:
    path = Path(Transaction[2:5], Criminal)
    select(path)

# if {:x} to ({Transfer amt > 7M} to {Transfer amt > 3M}) 2..5 to {:y}
#     return x, y
with graph.query() as select:
    x, y = Node(), Node()
    t1 = Transfer(); t1.amount > 7000000
    t2 = Transfer(); t2.amount > 3000000

    sub = Path(t1, t2)
    path = Path(x, sub[2:5], y)
    select(x, y)
```

## Functions

```python

@rai.fn
def greet(person:Person)
    return "Hello, ${person.name}"

with graph.query() as select:
    p = Person()
    select(p, greet(p))


# Aggregates example

from rai.aggregates import count, lowest

@rai.fn
def least_busy_team_member(team:Team):
    member = team.member
    num_tasks = count(member.tasks, per=member)
    lowest(num_tasks)
    return member

with graph.query() as select:
    t = Team()
    select(t, least_busy_team_member(t))

```

## Conditions

```python
# Equivalent to consecutive if statements

with graph.rule():
    with p.age >= 18:
        p.set(Adult)
    with p.age < 18:
        p.set(Minor)

# Equivalent to if/else

with graph.rule():
    with graph.cond():
        with p.age >= 65:
            p.set(Senior)
        with p.age >= 18:
            p.set(Adult)
        with p:
            p.set(Minor)
```

## Not

```python
with graph.rule():
    p = person
    with graph.not_found():
        Path(p, Edge[1:3], Crime)
    p.set(TotallyInnocent)

```

## Every

```python

with.graph.query() as select:
    p = Person()
    with graph.every(p):
        Dog() in p.pets
    select("Every person has a dog")

with graph.query() as select:
    p = Person()
    with graph.every(p):
        with graph.every(p.pet):
            Dog() in p.pets
    select("Every person has a pet, and every pet is a dog")

with graph.query() as select:
    p = Person()
    Dog() in p.pets
    with graph.every(p):
        Dog(name="Henry") in p.pets
    select("Every person with a dog, has a dog named henry")

with graph.query() as select:
    p = Person()
    Dog() in p.pets
    with graph.every(p.pets):
        p.pets.name == "Henry"
    select(p, "Every dog this person has is named henry")

```

## Integrating with Rel / Relations

```python
rel = graph.rel

with graph.rule():
    x = rel.range(1, 10, 1)
    rel.foo += (x, x * 100)

with graph.rule():
    x, y = graph.Vars(2)
    rel.foo(x, y)
    rel.bar += (x, y, x + y)
```