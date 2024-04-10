<!-- markdownlint-disable MD024 -->

# `relationalai.Instance`

Instances are [producers](../Producer/README.md) that produce the internal IDs of objects in a model.
You create instances by calling a [`Type`](../Type/README.md) object or the [`relationalai.std.Vars()`](../std/Vars.md) method,
which both return an instance of the `Instance` class.

```python
class relationalai.Instance(model: Model)
```

`Instance` is a subclass of [`Producer`](../Producer/README.md).

## Parameters

| Name | Type | Description |
| :--- | :--- | :------ |
| `model` | [`Model`](../Model/README.md) | The model in which the instance is created. |

## Methods

- [`Instance.persist()`](./persist.md)
- [`Instance.set()`](./set.md)
- [`Instance.unpersist()`](./unpersist.md)

## Example

Use [`Type`](../Type/README.md) objects and [`Model`](../Model/README.md) methods to create an `Instance` object
rather than constructing one directly:

```python
import relationalai as rai

model = rai.Model("people")
Person = model.Type("Person")

with model.rule():
    # The `Type.add()` method returns an `Instance` object.
    kermit = Person.add(name="Kermit")
    # `Instance` objects have a `.set()` method for setting properties.
    kermit.set(favorite_color="green")

with model.query() as select:
    # Calling a `Type` object returns an `Instance` object.
    person = Person()
    response = select(person.name)

print(response.results)
# Output:
#      name
# 0  Kermit
```

The following all return `Instance` objects:

- [`relationalai.Type.add()`](../Type/add.md)
- [`relationalai.Type.__call__()`](../Type/call__.md)
- [`relationalal.std.Vars()`](../std/Vars.md)
