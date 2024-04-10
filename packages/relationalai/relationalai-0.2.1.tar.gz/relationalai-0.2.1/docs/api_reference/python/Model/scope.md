# `relationalai.Model.scope()`

```python
Model.scope(dynamic: bool = False) -> Context
```

Creates a sub-[`Context`](../Context/README.md) that can be used to select objects
without restricting [producers](../Producer/README.md) in the surrounding context.

## Parameters

| Name | Type | Description |
| :--- | :--- | :------ |
| `dynamic` | `bool` | Whether or not the context is dynamic. Dynamic queries support Python control flow as macros. See [`Context`](../Context/README.md) for more information. |

## Returns

A [`Context`](../Context/README.md) object.

## Example

`Model.scope()` is a [context manager](https://docs.python.org/3/glossary.html#term-context-manager)
and should be called in a `with` statement.
It must be called from within a [rule](./rule.md) or [query](./query.md) context:

```python
import relationalai as rai

model = rai.Model("pets")
Person = model.Type("Person")
Dog = model.Type("Dog")
Cat = model.Type("Cat")

with model.rule():
    joe = Person.add(name="Joe")
    whiskers = Cat.add(name="Whiskers")
    miles = Dog.add(name="Miles")
    joe.set(pet=whiskers).set(pet=miles)

    jane = Person.add(name="Jane")
    spot = Cat.add(name="Spot")
    jane.set(pet=spot)

DogOwner = model.Type("DogOwner")
CatOwner = model.Type("CatOwner")

with model.rule():
    person = Person()
    with model.scope():
        # Restrict `person.pet` to `Dog` objects and
        # set the `DogOwner` type on `person`.
        Dog(person.pet)
        person.set(DogOwner)
    # Outside of the `with model.scope()` block, the
    # restriction on `person.pet` no longer applies.
    # `person` represents every person, not just people with pet dogs.
    with model.scope():
        Cat(person.pet)
        person.set(CatOwner)

# Joe is a dog owner.
with model.query() as select:
    dog_owner = DogOwner()
    response = select(dog_owner.name)

print(response.results)
# Output:
#   name
# 0  Joe

# Both Jane and Joe are cat owners.
with model.query() as select:
    cat_owner = CatOwner()
    response = select(cat_owner.name)

print(response.results)
# Output:
#    name
# 0  Jane
# 1   Joe
```

You may also write the above rule more compactly with `.scope()` by using the
[`Producer`](../Producer/README.md) objects returned by `Dog(person.pet)` and `Cat(person.pet)` as context managers:

```python
with model.rule()
    person = Person()
    with Dog(person.pet):
        person.set(DogOwner)
    with Cat(person.pet)
        person.set(CatOwner)
```

In most cases where you benefit from `Model.scope()`,
you may rewrite the rule or query more compactly using the [`Producer`](../Producer/README.md) object's context manager support
or one of the built-in context methods, like [`Model.found()`](./found.md) or [`Model.union()`](./union.md).

## See Also

[`Context`](../Context/README.md),
[`Model.found()`](./found.md),
[`Model.not_found()`](./not_found.md),
[`Model.ordered_choice()`](./ordered_choice.md),
and [`Model.union()`](./union.md).
