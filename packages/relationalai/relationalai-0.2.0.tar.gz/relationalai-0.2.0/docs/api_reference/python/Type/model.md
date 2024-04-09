# `relationalai.Type.model`

An attribute assigned to the [`Model`](../Model/README.md) to which the [`Type`](./README.md) belongs.

## Returns

A [`Model`](../Model/README.md) object.

## Example

```python
import relationalai as rai

model = rai.Model("myModel")
MyType = model.Type("MyType")

print(model == MyType.model)
# Output:
# True
```
