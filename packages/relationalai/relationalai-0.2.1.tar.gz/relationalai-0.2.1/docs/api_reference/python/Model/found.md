# `relationalai.Model.found()`

```python
relationalai.Model.found(dynamic: bool = False) -> Context
```

Creates a [`Context`](./Context/README.md) that restricts [producers](../Producer/README.md) in a [rule](./rule.md)
or [query](./query.md) to only those for which the conditions in the `.found()` context hold.

## Parameters

| Name | Type | Description |
| :--- | :--- | :------ |
| `dynamic` | `bool` | Whether or not the context is dynamic. Dynamic queries support Python control flow as macros. See [`Context`](./Context/README.md) for more information. |

## Returns

A [`Context`](../Context/README.md) object.

## Example

`Model.found()` is a [context manager](https://docs.python.org/3/glossary.html#term-context-manager)
and should be called in a `with` statement.
It must be called from within a [rule](./rule.md) or [query](./query.md) context:

```python
import relationalai as rai

model = rai.Model("people")
Person = model.Type("Person")

with model.rule():
    Person.add(name="Fred", age=22)
    Person.add(name="Janet", age=63)

# `model.found()` is always called in a nested `with` block
# inside of a `model.rule()` or `model.query()` context.
with model.query() as select:
    person = Person()
    with model.found():
        person.age > 60
    response = select(person.name)

print(response.results)
# Output:
#     name
# 0  Janet
```

In the preceding example, `model.found()` restricts the `person` instance to objects with an `age` value greater than 60.
But it does so without exposing the `person.age` producer to the surrounding context.
In other words, the restriction of `person.age` to values greater than 60 only applies inside of the `model.found()` sub-context.

This is especially important to remember when objects have a property with multiple values:

```python
import relationalai as rai

model = rai.Model("people")
Person = model.Type("Person")
Dog = model.Type("Dog")
Bird = model.Type("Bird")

# Add people and pets to the model.
with model.rule():
    fred = Person.add(name="Fred", age=22)
    janet = Person.add(name="Janet", age=63)
    mr_beaks = Bird.add(name="Mr. Beaks")
    spot = Dog.add(name="Spot")
    buddy = Dog.add(name="Buddy")
    # Fred has one pet and Janet has two.
    fred.set(pet=buddy)
    janet.set(pet=spot).set(pet=mr_beaks)

# What are the names of all pets of bird owners?
with model.query() as select:
    person = Person()
    # Restrict `person` to objects with a `pet` property
    # set to an object in the `Bird` type.
    with model.found():
        person.pet == Bird()
    response = select(person.name, person.pet.name)

print(response.results)
# Output:
#     name      name2
# 0  Janet  Mr. Beaks
# 1  Janet       Spot
```

Janet is the only person in the results because she is the only person with a pet bird.
Both of her pets, Spot and Mr. Beaks, appear in the results because the restriction
of `person.pet` to the `Bird` type only applies inside the `with model.found()` block.

Contrast that to the following query:

```python
with model.query() as select:
    person = Person()
    person.pet == Bird()
    response = select(person.name, person.pet.name)

print(response.results)
# Output:
#     name      name2
# 0  Janet  Mr. Beaks
```

Only Mr. Beaks appears because `person.pet == Bird()` restricts `person.pet` to the `Bird` type.

## See Also

[`Context`](./Context/README.md) and [`Model.not_found()`](./not_found.md)
