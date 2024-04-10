import relationalai as rai
from relationalai.std.graphs import Graph

model = rai.Model("socialNetwork2", config=globals()["test_config"])
Person = model.Type("Person")

# Add some people to the model and connect them with a `follows` property.
with model.rule():
    alice = Person.add(name="Alice")
    bob = Person.add(name="Bob")
    carol = Person.add(name="Carol")
    alice.set(follows=carol)
    bob.set(follows=alice)
    carol.set(follows=alice).set(follows=bob)

# Create a graph and add all Person objects to the set of nodes
# and the Person.follows property to the set of edges.
graph = Graph(model)
graph.Node.extend(Person)
graph.Edge.extend(Person.follows)

# Compute the PageRank of each person in the graph.
with model.query() as select:
    person = Person()
    centrality = graph.compute.pagerank(person)
    response = select(person.name, centrality)
