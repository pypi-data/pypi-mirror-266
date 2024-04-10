#pyright: reportUnusedExpression=false
import relationalai as rai
from relationalai.std import rel, Vars

model = rai.Model("MyCoolDatabase")
model.load_raw("rel/bar.rel")
model.load_raw("rel/foo.rel")

with model.query() as select:
    a,b = Vars(2)
    rel.foo(a, b)
    rel.bar(a + 5)
    z = select(a, b)

print(z.results)






