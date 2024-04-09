# `relationalai.Expression`

Expressions are [producers](./Producer/README.md) that produce the results of
a mathematical expression involving one or more [`Producer`](./Producer/README.md) objects.
You create expressions using operators like
[`+`](./Producer/add__.md),
[`==`](./Producer/eq__.md),
and [`>`](./Producer/gt__.md)
with a [`Producer`](./Producer/README.md) object, all of which return an instance of the `Expression` class.

```python
class Expression(model: Model)
```

`Expression` is a subclass of [`Producer`](./Producer/README.md).

## Parameters

| Name | Type | Description |
| :--- | :--- | :------ |
| `model` | [`Model`](./Model/README.md) | The model in which the expression is created. |

## Example

You create an `Expression` object when you use an operator like [`>`](./Producer/gt__.md)
with a [`Producer`](./Producer/README.md) object:

```python
import relationalai as rai

model = rai.Model("people")
Person = model.Type("Person")

with model.rule():
   Person.add(name="Fred", age=39)
   Person.add(name="Wilma", age=36)

with model.query() as select:
    person = Person()
    # Restrict `person.age` to values strictly greater than 36
    # and return an `Expression` object.
    person.age > 36
    response = select(person.name)

print(response.results)
# Output:
#    name
# 0  Fred
```

The following operators can all be used with [`Producer`](./Producer/README.md) objects to create `Expression` objects:

- [`+`](./Producer/add__.md)
- [`-`](./Producer/sub__.md)
- [`*`](./Producer/mul__.md)
- [`**`](./Producer/pow__.md)
- [`/`](./Producer/truediv__.md)
- [`==`](./Producer/eq__.md)
- [`!=`](./Producer/ne__.md)
- [`>`](./Producer/gt__.md)
- [`>=`](./Producer/ge__.md)
- [`<`](./Producer/lt__.md)
- [`<=`](./Producer/le__.md)

## See Also

[`Producer`](./Producer/README.md)
