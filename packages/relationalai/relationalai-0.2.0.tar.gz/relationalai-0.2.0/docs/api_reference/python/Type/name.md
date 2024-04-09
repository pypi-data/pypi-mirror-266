# `relationalai.Type.name`

An attribute assigned to the name of the type.

## Returns

A [`string`](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str) object.

## Example

```python
import relationalai as rai

model = rai.Model("myModel")
MyType = model.Type("MyType")

print(MyType.name)
# Output:
# 'MyType'
```
