# Getting Started With RelationalAI

Ready to dive into RelationalAI?
This document will quickly get you up and running.

## Install The `relationalai` Python Package

### Quick Start

To install the `relationalai` package:

```sh
pip install relationalai
```

If you use another Python package management solution (such as Conda, Poetry, etc.), use whichever command is appropriate for installing PyPI packages in your environment.

### Full Guide

> [!IMPORTANT]
> RelationalAI is compatible with Python version 3.10, 3.11, and 3.12.
> Visit [https://www.python.org/downloads/](https://www.python.org/downloads/)
> to download a compatible version of Python.

```sh
# Check your Python version.
python --version
```

If the above command fails or displays a version other than 3.10, 3.11, or 3.12,
you will need to install a compatible version of Python. You may need to use
a command like `python3` or `python3.10` or `python3.11` or `python3.12`
instead of the `python3` command. If one of those two commands works, use it
instead of `python3` in subsequent steps.

```sh
# Create a virtual environment.
python -m venv .venv
source .venv/bin/activate # On Windows use `.venv\Scripts\activate`

# Install the relationalai package.
python -m pip install relationalai
```

> [!TIP]
> If you would prefer not to activate your virtual environment every time you work on your project,
> you can reference the executables in your virtual environment directly.
> For example, you can use `./.venv/bin/python` instead of `python` and `./.venv/bin/rai` instead of `rai`.

Then, use the included `rai` CLI to initialize your project:

```sh
rai init  # Or .venv/bin/rai init, see caution callout below.
```

Follow the prompts to connect to your cloud platform
and configure your project's resources. You can inspect the status of your
configuration at any time by running `rai config:explain`.

> [!CAUTION]
> If you encounter an error saying that `init` is not a valid command,
> you may have the [original RelationalAI CLI](https://github.com/RelationalAI/rai-cli/) installed.
> If you no longer need the original CLI, you can delete it to resolve the error.
> To keep both CLIs, you may either rename the original CLI or use the command
> `/path/to/project/.venv/bin/rai` instead of `rai` to run the new CLI.
>
> You may also encounter issues with workflows using the original CLI
> if you install `relationalai` in your global environment.
> Always using a project-specific virtual environment is highly recommended.
> See [Virtual Environments and Packages](https://docs.python.org/3/tutorial/venv.html)
> for a primer on Python virtual environments.

To update your install when new features are released,
activate your project's virtual environment and run the following:

```sh
python -m pip install --upgrade relationalai
```

You will need to restart your Python interpreter to use the updated package.

## Create a Model

A **model** consists of rules describing the properties of and relationships between entities from your data.
Models live in your data cloud and are queried using RelationalAI's declarative query builder.

Here's an example of a model of friendships between people:

```python
import relationalai as rai

# 1: Create a model named "people".
model = rai.Model("people")

# 2: Create a Person object type.
Person = model.Type("Person")

# 3: Populate the model with some people.
with model.rule():
    # Add some people to the model.
    alex = Person.add(name="Alex", age=19)
    bob = Person.add(name="Bob", age=47)
    carol = Person.add(name="Carol", age=17)
    deb = Person.add(name="Deb", age=17)

    # Add a `friend` property.
    carol.set(friend=deb)
    alex.set(friend=bob)
    # Note that `.set()` doesn't overwrite existing properties.
    alex.set(friend=carol)

# 4: Is Alex friends with someone that is at least 21 years old?
with model.query() as select:
    alex = Person(name="Alex")
    person = alex.friend
    person.age >= 21
    response = select(person.name)

# 5: Display the results. Note that `.results` is a pandas DataFrame.
print(response.results)
# Output:
#   name
# 0  Bob
```

Here's what's happening, step-by-step:

1. `model = rai.Model("friends")` creates a new model named `friends`.
   You use the `model` object to manage and query the model.

2. For instance, one of the things you can do with `model` is create new types,
   such as the `Person` type created with `model.Type("Person")`.
   Types represent _collections_ of objects.

3. Once you have a type, use the `model.rule()`
   [context manager](https://realpython.com/python-with-statement/)
   to write a **rule** that adds objects of that type to the model.
   Like Python's [`open()` function](https://docs.python.org/3/library/functions.html#open),
   `model.rule()` is used in a
   [`with` statement](https://docs.python.org/3/reference/compound_stmts.html#the-with-statement).
   Exiting the `with` block translates your rule into a RelationalAI query before sending it to the cloud.

   Inside of the `with model.rule()` block:

   A. `Person.add(name="Alex", age=23)` adds a new object to `Person` with
   a `name` property set to `"Alex"` and an `age` property set to `19`.
   Properties created with `.add()` are used to identify the object uniquely.
   All other properties should be created with `.set()`

   B. `alex.set(friend=bob)` creates a `.friend` property on `alex`.
   Calling `alex.set(friend=carol)` adds `carol` to the `friend` property without removing `bob`.
   This is because properties created with `.set()` behave like sets.

4. With some data in your model, you're ready to query.
   This query asks for the names of all of Alex's friends who are at least 21 years old:

   ```python
   # `with model.query()` begins a new query.
   # `select` is used later to select query results.
   with model.query() as select:

       # Find all people named Alex.
       alex = Person(name="Alex")

       # Get all of Alex's friends.
       person = alex.friend

       # Filter those people by age at least 21.
       person.age >= 21

       # Select the friends' names.
       response = select(person.name)
   ```

   First, `alex = Person(name="Alex")` finds all `Person` objects with a `name` property equal to `"Alex"`.
   In this case, there is only one person named Alex.
   But keep in mind that `alex` is really a _set_.
   Then, `person = alex.friend` gets every person that Alex is friends with.

   But what's going on in the line `person.age >= 21`?
   Shouldn't that return `True` or `False`,
   and shouldn't you _use_ that value somewhere?

   This is where we see the difference between
   Python's _imperative_ view of the world
   and RelationalAI's _declarative_ view.
   You can think of the `>=` operator as filtering `person` in-place
   to only those people with an `age` property that satisfies the condition.
   That's the imperative worldview.
   From a declarative perspective,
   you can read each line as a constraint on the results,
   with everything joined together by `and`:

   | Python | Declarative Interpretation |
   | :--- | :------ |
   | `alex = Person(name="Alex")` | `alex` is a `Person` with a `name` property equal to `"Alex"`. |
   | `person = alex.friend` | AND `person` is a friend of `alex`. |
   | `person.age >= 21` | AND `person` has an `age` property greater than `21`. |

> [!TIP]
> Whenever you see a `with model.rule()` or `with model.query()` block,
> it's time to think declaratively.

5. Finally, `response.results` is used to access the results as a pandas DataFrame.
   This puts all of pandas' features at your fingertips to further analyze, plot, or transform your data.

> [!NOTE]
> When a `with model.query()` block terminates,
> the query builder translates your Python into a RelationalAI query, executes it,
> and blocks until results are returned or an exception is raised.

## Query Your Model

Let's take a closer look at some basic queries.

### Retrieve Objects

Types, like `Person`, are used to retrieve objects from a model.
For example, the following query finds all people and returns their names:

```python
with model.query() as select:
    person = Person()
    response = select(person.name)

print(response.results)
# Output:
#     name
# 0   Alex
# 1    Bob
# 2  Carol
# 3    Deb
```

To find objects with specific properties, pass the property name and value to `Person()`:

```python
with model.query() as select:
    person = Person(age=17)
    response = select(person.name, person.age)

print(response.results)
# Output:
#     name age
# 0  Carol  17
# 1    Deb  17
```

### Filter Objects

You can filter objects by their properties using logical operators like `==`, `!=`, `<`, and `<=`.
For instance, to find all teenagers in the model, first get all people and then filter by their `.age` property:

```python
with model.query() as select:
    teenager = Person()
    13 <= teenager.age <= 19
    response = select(teenager.name, teenager.age)

print(response.results)
# Output:
#     name age
# 0   Alex  19
# 1  Carol  17
# 2    Deb  17
```

In the next query, `!=` is used to find all people whose name isn't Bob:

```python
with model.query() as select:
    not_bob = Person()
    not_bob.name != "Bob"
    response = select(not_bob.name)

print(response.results)
#      name
# 0    Alex
# 1   Carol
# 2     Deb
```

This works because people only have one name.
If a property has multiple values, like the `.friend` property, you need to be careful:

```python
with model.query() as select:
    person = Person()
    person.friend.name != "Bob"
    response = select(person.name)

print(response.results)
#     name
# 0   Alex
# 1  Carol
```

Here, `person.friend.name != "Bob"` says that `person` has a `.friend` property with a `.name` property that isn't `"Bob"`.
This includes Alex since he's friends with Carol.
If you want to find people who don't know _anyone_ named Bob,
use the `model.not_found()` context manager:

```python
with model.query() as select:
    person = Person()
    with model.not_found():
        person.friend.name == "Bob"
    response = select(person.name)

print(response.results)
#     name
# 0    Bob
# 1  Carol
# 2    Deb
```

Carol, who is friends with Deb, still shows up.
Bob and Deb, who don't have a `.friend` property, are also included in the results.

### Combine Filters

You may combine multiple filters in the same query:

```python
with model.query() as select:
    person = Person()
    person.age <= 21
    person.friend.age > 40
    response = select(person.name, person.friend.name)

print(response.results)
# Output:
#    name name2
# 0  Alex   Bob
```

Here, `person.age <= 21` filters `person` to all people at most 21 years old.
Then `person.friend.age > 40` filters `person.friend` to all people over 40.
Since Alex is the only person under 21 who is friends with someone over 40,
and Bob is the only person over 40 that Alex is friends with,
the pair `Alex, Bob` is the only pair in the results.

To get _every_ friend, not just friends with an `.age` property greater than `40`,
you can use the `model.found()` context manager:

```python
with model.query() as select:
    person = Person()
    person.age <= 21
    with model.found():
        person.friend.age > 40
    response = select(person.name, person.friend.name)

print(response.results)
# Output:
#     name  name2
# 0   Alex    Bob
# 1   Alex  Carol
```

### Sort Results

If you just need to sort the results of a query, you can use pandas' `.sort_values()` method:

```python
with model.query() as select:
    person = Person()
    response = select(person.name, person.age)

print(response.results.sort_values(by="age"))
# Output:
#     name  age
# 2  Carol   17
# 3    Deb   17
# 0   Alex   19
# 1    Bob   47
```

In some cases, though, you may need to use the sort order in the query itself.
Or, you may need to sort a collection that is too big for a DataFrame.
To sort results inside of a query, use `aggregates.rank_asc()` or `.rank_desc()`:

```python
from relationalai.std import aggregates

with model.query() as select:
    person = Person()
    rank = aggregates.rank_asc(person.age, person)
    response = select(rank, person.name, person.age)

print(response.results)
# Output:
#    v   name  age
# 0  1  Carol   17
# 1  2    Deb   17
# 2  3   Alex   19
# 3  4    Bob   47
```

You must pass `person.age` _and_ `person` to `.rank_asc()` because there may be
(and, in fact, are) multiple people with the same age.
`.rank_asc(person.age)` sorts the _set_ of all people's ages:

```python
from relationalai.std import aggregates

with model.query() as select:
    person = Person()
    rank = aggregates.rank_asc(person.age)
    response = select(rank, person.name, person.age)

print(response.results)
# Output:
#    v   name  age
# 0  1  Carol   17
# 1  1    Deb   17
# 2  2   Alex   19
# 3  3    Bob   47
```

Note that Carol and Deb both have `rank` equal to `1`.

Instead, `.rank_asc(person.age, person)` sorts _pairs_ of ages and people.
If two people have the same age, `person` is used to disambiguate.

### Customize Result Column Names

In the preceding example, `select(rank, person.name, person.age)` returns results
with columns named `v`, `name`, and `age`.
Property names are automatically used as column names.
But `rank` isn't a property, so its column is given the generic name `v`.

You may provide custom column names using `relationalai.std.alias()`:

```python
from relationalai.std import aggregates, alias

with model.query() as select:
    person = Person()
    rank = aggregates.rank_asc(person.age, person)
    response = select(alias(rank, "rank"), person.name, person.age)

print(response.results)
# Output:
#    rank   name  age
# 0     1  Carol   17
# 1     2    Deb   17
# 2     3   Alex   19
# 3     4    Bob   47
```

### Aggregate and Group Results

Just like sorting, you can use pandas DataFrame methods to aggregate and group results:

```python
with model.query() as select:
    person = Person()
    response = select(person.name, person.age)

# Use pandas `.mean()` to find the average age of people in the model.
print(response.results.age.mean())
# Output:
# 25.0
```

But sometimes you need to use aggregate values in queries.
Aggregate methods are available in the `relationalai.std.aggregates` namespace.
For instance, to find the average age of all people in the model, use `avg()`:

```python
from relationalai.std import aggregates

with model.query() as select:
    person = Person()
    avg_age = aggregates.avg(person, person.age)
    response = select(avg_age)

print(response.results)
# Output:
#       v
# 0  25.0
```

You must pass `person` _and_ `person.age` to `.avg()` because `person.age` is a _set_
and there are multiple people in the model with the same age.
For instance, `.avg(person.age)` aggregates over the _set_ of ages and so won't count `17` twice for both Carol and Deb.
In contrast, `.avg(person, person.age)` aggregates over the set of _pairs_ of people and ages.
The aggregation is done over the last positional parameter.

You may group results using an aggregate method's `per` parameter:

```python
from relationalai.std import aggregates

with model.query() as select:
    person = Person()
    avg_friend_age = aggregates.avg(person.friend, person.friend.age, per=[person])
    response = select(person.name, avg_friend_age)

print(response.results)
# Output:
#     name     v
# 0   Alex  32.0
# 1  Carol  17.0
```

Bob and Deb are excluded from the results because neither has a `.friend` property.

## Add Reasoning With Rules

You can use the same query builder syntax used in `with model.query()` blocks in a `.rule()` block.
The difference is that instead of returning query results, rules modify the model by calling `.add()` or `.set()`.

For example, you can use a rule to tag people that have an `.age` property less than `18` with a `Minor` type:

```python
Minor = model.Type("Minor")

with model.rule():
    person = Person()
    person.age < 18
    person.set(Minor)
```

Then you can use `Minor` in queries, just like the `Person` type:

```python
with model.query() as select:
    minor = Minor()
    response = select(minor.name, minor.age)

print(response.results)
# Output:
#     name  age
# 0  Carol   17
# 1    Deb   17
```

You may also use rules to add relationships implied by but not explicitly contained in the data.
For instance, the `.friend` property really represents a bidirectional relationship between people.
If Alex is with friends with Bob, then Bob is friends with Alex.

Here's a rule that extends the model with the missing relationships:

```python
with model.rule():
    person = Person()
    person.friend.set(friend=person)
```

Now, every person is friends with somebody else:

```python
from relationalai.std import aggregates

with model.query():
    person = Person()
    friend_count = aggregates.count(person.friend, per=[person])
    response = select(person.name, friend_count)

print(response.results)
# Output:
#     name  v
# 0   Alex  2
# 1    Bob  1
# 2  Carol  2
# 3    Deb  1
```

## Next Steps

In this getting started guide, you saw how to create a model, describe it with rules,
and query it using RelationalAI's declarative query builder.
API reference, more examples, and other learning materials are coming soon!
