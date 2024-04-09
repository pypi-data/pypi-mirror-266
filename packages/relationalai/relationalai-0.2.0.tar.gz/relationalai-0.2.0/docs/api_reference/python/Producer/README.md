<!-- markdownlint-disable MD024 -->

# Producer

`Producer` objects represent an unknown value in a context.
When a [query](../Model/query.md) context is evaluated,
the values matching the context's constraints are produced.
The `Producer` class is the base class for different types of producers,
such as [`Instance`](../Instance/README.md) objects, which produce the IDs of objects in your model,
or [`InstanceProperty`](../InstanceProperty/README.md) objects, which produce object property values.

```python
class Producer(model: Model)
```

## Parameters

| Name | Type | Description |
| :--- | :--- | :------ |
| `model` | [`Model`](../Model/README.md) | The model in which the producer is created. |

## Methods

- [`Producer.__add__()`](./add__.md)
- [`Producer.__enter__()`](./enter__.md)
- [`Producer.__eq__()`](./eq__.md)
- [`Producer.__exit__()`](./exit__.md)
- [`Producer.__ge__()`](./ge__.md)
- [`Producer.__getattribute__()`](./getattribute__.md)
- [`Producer.__gt__()`](./gt__.md)
- [`Producer.__le__()`](./le__.md)
- [`Producer.__lt__()`](./lt__.md)
- [`Producer.__mul__()`](./mul__.md)
- [`Producer.__ne__()`](./ne__.md)
- [`Producer.__pow__()`](./pow__.md),
- [`Producer.__radd__()`](./radd__.md)
- [`Producer.__rmul__()`](./rmul__.md)
- [`Producer.__rpow__()`](./rpow__.md),
- [`Producer.__rsub__()`](./rsub__.md)
- [`Producer.__rtruediv__()`](./rtruediv__.md)
- [`Producer.__sub__()`](./sub__.md)
- [`Producer.__truediv__()`](./truediv__.md)

## Example

`Producer` objects show up all over the place:

```python
import relationalai as rai

model = rai.Model("people")
Person = model.Type("Person")

with model.rule():
    # `Type.add()` returns an `Instance` object, which is a `Producer`.
    fred = Person.add(name="Fred", age=39)
    fred.set(favorite_color="green")

with model.query() as select:
    # Calling a Type returns an `Instance`.
    person = Person()

    # Accessing a property returns an `InstanceProperty` object,
    # which is a `Producer`.
    name = person.name
    age = person.age

    # Operators return an `Expression` object, which is a `Producer`.
    age > 30

    response = select(name, age)

print(response.results)
# Output:
#    name  age
# 0  Fred   39
```

The following classes are all subclasses of `Producer`:

- [`Instance`](../Instance/README.md)
- [`InstanceProperty`](../InstanceProperty/README.md)
- [`Expression`](../Expression.md)
