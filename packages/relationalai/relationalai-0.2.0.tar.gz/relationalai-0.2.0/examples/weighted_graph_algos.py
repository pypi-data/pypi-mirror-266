# pyright: reportUnusedExpression=false
import relationalai as rai
from relationalai.std.graphs import Graph
from relationalai.std.aggregates import sum

#--------------------------------------------------
# Types
#--------------------------------------------------

model = rai.Model("MyCoolDatabase")
Person = model.Type("Person")
Transaction = model.Type("Transaction")

#--------------------------------------------------
# Load data
#--------------------------------------------------

with model.rule():
    joe = Person.add(name="Joe")
    jane = Person.add(name="Jane")
    bob = Person.add(name="Bob")
    dylan = Person.add(name="Dylan")
    susan = Person.add(name="Susan")

    Transaction.add(from_=joe, to=jane, amount=100)
    Transaction.add(from_=joe, to=jane, amount=1000)
    Transaction.add(from_=joe, to=jane, amount=10)
    Transaction.add(from_=joe, to=bob, amount=10)
    Transaction.add(from_=susan, to=dylan, amount=10)

#--------------------------------------------------
# Graph
#--------------------------------------------------

graph = Graph(model, weighted=True)

with model.rule():
    t = Transaction()
    # Aggregate the amounts of all txns between two people
    # @NOTE: Be careful not to specify multiple weights for a single edge, that can lead to no results!
    weight = sum(t, t.amount, per=[t.from_, t.to])
    graph.Edge.add(t.from_, t.to, label="Transfer", weight=weight)

with model.query() as select:
    p = Person()
    community_id = graph.compute.louvain(p)
    res = select(p.name, community_id)

print(res)
