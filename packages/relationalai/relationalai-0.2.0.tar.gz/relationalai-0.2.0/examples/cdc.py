#pyright: reportUnusedExpression=false
from typing import Tuple
import relationalai as rai
from relationalai.clients.snowflake import Snowflake

model = rai.Model("MyCoolDatabase", dry_run=False)
sf = Snowflake(model)
Person = sf.sandbox.public.person
Address = sf.sandbox.public.address
Address.describe(
    personid=(Person, "person")
)

with model.rule():
    a = Address()
    a.personid > 0
    a.set(coolness=a.personid * 10)

with model.query() as select:
    a = Address()
    z = select(a.address, a.person.firstname, a.coolness)

@model.export("sandbox.public")
def my_analysis(personid: int) -> Tuple[str, int]:
    a = Address(
        person = Person(personid=personid)
    )
    return a.person.firstname, a.coolness

print("People!\n")
print(z.results)

print("\nCalling my analysis from Snowflake!\n")
for row in model.resources._exec("call sandbox.public.my_analysis(1);"):
    print(row)







