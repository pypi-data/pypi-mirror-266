from gentest.emit import Document
import relationalai as rai
from relationalai.clients.test import Executor, Install, Query

graph = rai.clients.test.Graph("emit_playground")

Person = graph.Type("Person")
Adult = graph.Type("Adult")
Card = graph.Type("Card")

Person.add(name="Joe", age=54)
# Person.add(name="Bob", age=40)
# Person.add(name="Jane", age=10)

with graph.rule():
    p = Person()
    p.age
    p.set(Adult, name="Jeff")
    Card.add(name="Business", paper_color="ivory")
    # p.age > 18
    #p.set(Adult)


# with graph.query() as select:
#     p = Person();
#     res = select(p, p.name, p.age)



exec = graph._client
assert isinstance(exec, Executor)
print(str(exec))

doc = Document()

for block in exec.blocks:
    match block:
        case Install():
            doc.rule(block.task)
        case Query():
            doc.query(block.task)

h = "==[ Emit ]"
print(f"{h}{'='*(80-len(h))}")
print(doc.stringify())
