# `relationalai.Instance.unpersist()`

```python
relationalai.Instance.unpersist(*args, **kwargs) -> Instance
```

Unpersists types and properties on objects set with [`.persist()`](./persist.md)
and returns the unpersisted [`Instance`](./unpersist.md).
`.unpersist()` is not typically used and should only be called by advanced users.

## Parameters

| Name | Type | Description |
| :--- | :--- | :------ |
| `*args` | [`Type`](../Type/README.md) | The type(s) to remove from the `Instance`. |
| `*kwargs` | `Any` | Property values to remove from the `Instance`. |

## Returns

An [`Instance`](./README.md) object.

## Example

```python
import relationalai as rai

model = rai.Model("people")
Person = model.Type("Person")

# Add an object to the `Person` type and persist a
# `favorite_color` property using the `.persist()` method.
with model.rule():
    fred = Person.add(name="Fred")
    fred.persist(favorite_color="green")

# Unpersist the property set in the preceding rule.
with model.rule():
    fred = Person(name="Fred")
    fred.unpersist(favorite_color="green")
```

## See Also

[`Instance.persist()`](./persist.md)
