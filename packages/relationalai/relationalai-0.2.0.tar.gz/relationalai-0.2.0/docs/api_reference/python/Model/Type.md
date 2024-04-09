# `relationalai.Model.Type()`

```python
relationalai.Model.Type(name: str) -> Type
```

Creates a new [Type](../Type/README.md) in the model.

#### Parameters

| Name | Type | Description |
| :--- | :--- | :------ |
| `name` | `str` | The name of the type. Type names must begin with a Unicode letter or an underscore followed by one or more Unicode letters, underscores, or numbers. |

#### Returns

A [`Type`](../Type/README.md) object.

#### Example

```python
import relationalai as rai

model = rai.Model("people")

Person = model.Type("Person")
```

#### See Also

[`Type`](../Type/README.md)
