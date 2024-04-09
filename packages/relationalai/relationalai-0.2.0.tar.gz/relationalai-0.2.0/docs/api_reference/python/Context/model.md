# `relationalai.Context.model`

An attribute assigned to the [`Model`](../Model/README.md) object for which the context was created.

## Returns

A [`Model`](../Model/README.md) object.

## Example

```python
import relationalai as rai

model = rai.model("people")
Person = model.Type("Person")

with model.query() as select:
    person = Person()
    response = select(person.name)

# `response` is the `Context` object created by `model.query()`.
print(response.model == model)
# Output:
# True
```

Calling a [`ContextSelect`](../ContextSelect/README.md) object, like `select` in the preceding query, returns its `Context` object.
In this case, `response` is the `Context` object created by [`model.query()`](../Model/query.md) in the `with` statement.

## See Also

[`Model`](../Model/README.md)
