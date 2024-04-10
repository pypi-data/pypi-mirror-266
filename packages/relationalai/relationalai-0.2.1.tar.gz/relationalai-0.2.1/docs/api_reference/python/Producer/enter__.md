# `relationalai.Producer.__enter__()`

```python
relationalai.Producer.__enter__() -> None
```

[`Producer`](./README.md) objects can be used as [context managers](https://docs.python.org/3/glossary.html#term-context-manager)
in a [`with` statement](https://docs.python.org/3/reference/compound_stmts.html#with)
to apply restrictions in a [rule](../Model/rule.md) or [query](../Model/query.md) conditionally.
In a `with` statement, Python calls the context manager's `.__enter__()` method before executing the `with` block.
After the `with` block executes,
the `with` statement automatically executes the [`Producer.__exit__()`](./exit__.md) method.

## Parameters

None.

## Returns

`None`.

## Example

You may use `Producer` objects in a `with` statement to set a property or Type conditionally:

```python
import relationalai as rai

model = rai.Model("people")
Person = model.Type("Person")
Adult = model.Type("Adult")

with model.rule():
    Person.add(name="Fred", age=39)
    Person.add(name="Wilma", age=36)
    Person.add(name="Pebbles", age=6)

# People who 18 years old or older are adults.
with model.rule():
    person = Person()
    with person.age >= 18:
        person.set(Adult)

with model.query() as select:
    adult = Adult()
    response = select(adult.name, adult.age)

print(response.results)
# Output:
#     name  age
# 0   Fred   39
# 1  Wilma   36
```

The `with person.age >= 18` block temporarily restricts `person.age` to values greater than or equal to 18.
After Python executes the `with` block, the [`Producer.__exit__()`](./exit__.md) method is called to remove the restriction.
This allows you to write multiple conditional `with` statements
in the same [rule](../Model/rule.md) or [query](../Model/query.md):

```python
Child = model.Type("Child")

with model.rule():
    person = Person()
    with person.age >= 18:
        person.set(Adult)
    with person.age < 18:
        person.set(Child)

with model.query() as select:
    child = Child()
    response = select(child.name, child.age)

print(response.results)
# Output:
#       name  age
# 0  Pebbles    6
```

## See Also

[`Context](../Context/README.md) and [`Producer.__exit__()`](./exit__.md).
