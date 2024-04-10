# `relationalai.Instance.set()`

```python
Instance.set(*args, **kwargs) -> Instance
```

Sets types and properties on an [`Instance`](./README.md) object and returns the `Instance`.

## Parameters

| Name | Type | Description |
| :--- | :--- | :------ |
| `*args` | [`Type`](../Type/README.md) | The type(s) to which the `Instance` belongs. |
| `*kwargs` | `Any` | Properties and values to set on the `Instance`. |

## Returns

An [`Instance`](./README.md) object.

## Example

```python
import relationalai as rai

model = rai.Model("people")
Person = model.Type("Person")

with model.rule():
    fred = Person.add(name="Fred")
    fred.set(favorite_color="green", favorite_food="pizza")
```

The rule in the preceding example adds an object identified by the name `"Fred"` to the model and sets
a `favorite_color` property to the string `"green"` and a `favorite_food` property to the string `"pizza"`.

You set object properties with [`Type.add()`](../Type/add.md) and `Instance.set()`.
The difference is that properties set by `Type.add()` uniquely identify the object.

`.set()` returns an `Instance`, which means you may chain calls to `.set()` to add multiple property values:

```python
with model.rule():
    fred = Person.add(name="Fred")
    fred.set(favorite_color="green").set(favorite_color="blue")
```

This version of the rule sets two values to the `favorite_color` property.
Setting a new value on a property does not override existing values.

## See Also

[`Type.add()`](../Type/add.md)
