# `relationalai.Instance.persist()`

```python
relationalai.Instance.persist(*args, **kwargs) -> Instance
```

Persists types and properties on an object and returns the persisted [`Instance`](./README.md).
`.persist()` is not typically used and should only be called by advanced users.

## Parameters

| Name | Type | Description |
| :--- | :--- | :------ |
| `*args` | [`Type`](../Type/README.md) | The type(s) to which the `Instance` is persisted. |
| `*kwargs` | `Any` | Properties and values to persist on the `Instance`. |

## Returns

And [`Instance`](./README.md) object.

## Example

```python
import relationalai as rai

model = rai.Model("people")
Person = model.Type("Person")

with model.rule():
    fred = Person.add(name="Fred")
    fred.persist(favorite_color="green")
```

A `Person` object with a `favorite_color` property set to `"green"` persists in the model
even if you delete the [rule](../Model/rule.md) that adds it.
You may remove persisted object properties using [`Instance.unpersist()`](./unpersist.md).

## See Also

[`Instance.unpersist()`](./unpersist.md)
