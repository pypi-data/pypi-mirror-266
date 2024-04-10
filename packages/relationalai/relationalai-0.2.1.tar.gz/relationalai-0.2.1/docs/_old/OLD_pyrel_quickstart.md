# Quickstart

This quickstart takes you through the basic building blocks of PyRel: objects, rules, and functions. We'll walkthrough a simple banking fraud example to ground ourselves. Here's what it'll look like by the end, just to give you a sense of what PyRel is like.

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



## Objects

PyRel is a relational language, which means that under the covers everything is represented as normalized tables, but that can be quite hard to work with. So instead, PyRel presents us with objects, which you can think of as being similar to JSON objects with a little bit of sugar to make working with them nicer. As an example, let's add a couple of objects into our system.

```python
Person = graph.Type("Person")

Person.add(name="Joe", age=30)
Person.add(name="Jane", age=30)
```

By convention we capitalize the types of objects (e.g Person, Student, Employee) and like in JSON, these objects can be nested:

```python
Person.add(name="Derek", age=26, pet=Dog.add(name="Henry"))
```

And since types are represented as boolean properties internally, there's no problem with having multiple. For example, we can say that Sweta is Person and a Student, by passing the student type to the Person constructor:

```python
Person.add(Student, name="Swetha", age=14)
```

## Rules
Now that we have data to work with, we want to be able to query it and do something with the results. Rules allow us to search for logical patterns and then specify what we'd like to happen if that pattern is found. Patterns look just like the objects we added above, so if we wanted to find all the people named Bob and get their age we could write:

```python
with graph.rule():
    bobs = Person(name="Bob")
    age = bobs.age
```

That pattern would find all the people with a name property equal to "Bob" and bind their age to an `age` variable. We could also add a constraint to find all the people named "Bob" that are under 18:

```python
with graph.rule():
    bobs = Person(name="Bob")
    bobs.age < 18
```

Great, so we have the ability to create patterns of objects to find, let's use that to create a rule that says any person under 18 is a minor:

```python
with graph.rule():
    p = Person(); p.age < 18
    p.set(Minor)
```

Rules always have this structure of `with graph.rule(): ... some patterns and actions ...` and they're automatically maintained by the system. Since PyRel is relational, actions take the form of changing data. So in this case, if a new person under the age of 18 is added they will have the `Minor` type added to them. Similarly if a person's age changes to be 18 or older, the `Minor` type will be removed from them. As long as all the patterns in the rule match, the person will be a Minor. That's the guarantee this rule makes.

We could add the equivalent rule for adults:

```python
with graph.rule():
    p = Person(); p.age >= 18
    p.set(Adult)
```

It's worth noting that this basically extends the person object with new types and properties, so for example we could set multiple types and properties at once:

```python
with graph.rule():
    p = Person(); p.age >= 18
    p.set(Adult, Voter, allowed_votes=1)
```

In some cases, you want to permanently say something about an object and not have the rule retract what it said if the conditions are no longer met. To do that you would use the `persist` action:

```python
with graph.rule():
    p = Person(); p.age < 18
    p.persist(Minor)
```

Now the `Minor` attribute will be added to any person under 18, but it won't be removed if they grow up. Instead you'd have to write a rule that removes it:

```python
with graph.rule():
    p = Person(); p.age >= 18
    p.unpersist(Minor)
```

In general, it's best to just make statements about the world and let the system handle keeping them up to date, but this power of complete control is there if you need it.

## Loading data and validating it

Let's breakdown a more sophisticated rule that loads some data about people from a CSV file:

```python
from rai import csv

with graph.rule():
    (name, age, account) = csv.load("people.csv")
    p = Person.ensure(name=name, age=age)
    with account:
        p.set(Customer, account=account)
```

We call the `csv.load` function to parse a CSV file into tuples per row. We then use the `ensure` function to find a person with the given name and age or insert a new one if they don't already exist.

```python
    p = Person.ensure(name=name, age=age)
```

This gives us a convenient way to map our CSV data to what we already have in the system, or add if it's new to us. Because both the found person and the added person are bound to the `p` variable, we can use that variable in the rest of the rule to correctly refer to whichever is chosen.

```python
    with account:
        p.set(Customer, account=account)
```

The last two lines then check if the optional account column was provided and if so, we reference our person object and extend it with a Customer property and the account value from the CSV. `with ...:` denotes a subrule where the conditions inside must match for its actions to take effect, just like the top level rule.

It's worth pointing out that PyRel doesn't allow nulls to enter the system. This is why we have to explicitly check that account exists before attempting to set the account property to it. If we didn't, the first time we tried to load a row without an account column, we'd get an error. This is a common pattern when working with external data sources that can often have missing information.

Now that we have a bunch of customers loaded, we want to make sure our data is correct. As an example validation, let's say that all customers must be adults:

```python
with graph.rule():
    Customer(Adult=False)
    Error.add(message="Customers must be adults")
```

By creating an `Error` object, we're telling the system that integrity has been violated and we should abort the current transaction. Because we can express validataion as just regular rules that produce `Error` objects, we have the full power of the language to express our intent.

## Analyzing data in Snowflake using graphs

As a coprocessor, we can also write rules that query data in our Snowflake databases. For example, we could write a rule that finds all transactions from a customer to a criminal and marks them as suspicious. To do that, our first step is to bring in some of our Snowflake tables.

```python
fraud = rai.snowflake.fraud
Criminal = graph.Type(fraud.Criminal)
Transaction = graph.Type(fraud.Transaction)
```

Snowflake tables are represented as typed objects, just like all the rest of the data in the system, so now that we have a reference to the properties that identify transactions and criminals, we can write the rule like normal:

```python
with graph.rule():
    t = Transaction(_from=Customer(), to=Criminal())
    t.set(Suspicious)
    with t.amount > 10000:
        t.set(ImmediateReview, review_reason="Large transaction to criminal")
```

We can also do some more sophisticated graph traversal. For example we can check for transactions that connect criminals in 2 hops or less and mark those for review. Transactions represent an edge with a number of properties on it, we can tell the graph to treat it as an edge by using the `object_edge` function and with `payer` and `payee` as the incoming node and outgoing node respectively:

```python
from rai.graph import shortest

Path = graph.Path
Transfer = graph.Edge(Transaction, Transaction.payer, Transaction.payee)

with graph.rule():
    c, c2 = Criminal(), Criminal()
    path = shortest(Path(c, Transfer[1:2], c2))
    start = path.edges[0]
    start.set(ImmediateReview, path=path, review_reason="Criminal to criminal transaction")
```

These two rules tell us which transactions we need to review, but our review systems query the `ReviewQueue` table in Snowflake, so we need to write our analysis back into that table. Fortunately, we can write to Snowflake in a very similar way to how we read from it; by using objects.

```python
ReviewQueue = graph.Type(fraud.ReviewQueue)

with graph.rule():
    t = Transaction.get(ImmediateReview)
    ReviewQueue.add(transaction=t, reason=t.review_reason, path=either(t.path, [t]))
```
