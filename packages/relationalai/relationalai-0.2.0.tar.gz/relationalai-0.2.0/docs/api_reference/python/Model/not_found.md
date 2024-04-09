# `relationalai.Model.not_found()`

```python
relationalai.Model.not_found(dynamic: bool = False) -> Context
```

Creates a [`Context`](../Context/README.md) that restricts [producers](../Producer/README.md) in a [rule](./rule.md) or [query](./query.md)
to only those values for which any of the conditions in the `.not_found()` context fail.

## Parameters

| Name | Type | Description |
| :--- | :--- | :------ |
| `dynamic` | `bool` | Whether or not the context is dynamic. Dynamic queries support Python control flow as macros. See [`Context`](../Context/README.md) for more information. |

## Returns

A [`Context`](../Context/README.md) object.

## Example

`Model.not_found()` is a [context manager](https://docs.python.org/3/glossary.html#term-context-manager)
and should be called in a `with` statement.
It must be called from within a [rule](./rule.md) or [query](./query.md) context:

```python
import relationalai as rai

model = rai.Model("people")
Person = model.Type("Person")

with model.rule():
    Person.add(name="Fred", age=22)
    Person.add(name="Janet", age=63)

# `model.not_found()` is always called in a nested `with` block
# inside of a `model.rule()` or `model.query()` context.
with model.query() as select:
    person = Person()
    # Restrict `person` to objects that do not have
    # a `name` property set to the string `"Janet"`.
    with model.not_found():
        person.name == "Janet"
    response = select(person.name)

print(response.results)
# Output:
#    name
# 0  Fred
```

## See Also

[`Context`](../Context/README.md) and [`model.found()`](./found.md)
