<!-- markdownlint-disable MD024 -->

# `relationalai.Context`

Contexts execute blocks of code written in RelationalAI's declarative query builder syntax.
You create contexts using [`Model`](../Model/README.md) methods,
such as [`Model.query()`](../Model/query.md) and [`Model.rule()`](../Model/rule.md),
that return an instance of the `Context` class.

```python
class relationalai.Context(model: Model, dynamic: bool = False)
```

## Parameters

| Name | Type | Description |
| :--- | :--- | :------ |
| `model` | [`Model`](../Model/README.md) | The model for which the context is created. |
| `dynamic` | `bool` | Whether or not the context is dynamic. Dynamic contexts support Python control flow as query builder macros. |

## Attributes

- [`Context.model`](./model.md)
- [`Context.results`](./results.md)

## Methods

- [`Context.__enter__()`](./enter__.md)
- [`Context.__exit__()`](./exit__.md)
- [`Context.__iter__()`](./iter__.md)

## Example

You create contexts using [`Model`](../Model/README.md) methods rather than creating a `Context` instance directly.
The primary contexts are [`Model.rule()`](../Model/rule.md) and [`Model.query()`](../Model/query.md).

`Context` objects are [context managers](https://docs.python.org/3/glossary.html#term-context-manager).
You use them in [`with` statements](https://docs.python.org/3/reference/compound_stmts.html#with):

```python
import relationalai as rai

model = rai.Model("myModel")
MyType = model.Type("MyType")

# Create a rule context with `model.rule()` that adds an object to `MyType`.
with model.rule():
    MyType.add(name="my first object")

# Create a query context with `model.query()` to query the model.
with model.query() as select:
    obj = MyType()
    response = select(obj.name)

print(response.results)
# Output:
#               name
# 0  my first object
```

The following `Model` methods all return `Context` objects:

- [`Model.found()`](../Model/found.md)
- [`Model.not_found()`](../Model/not_found.md)
- [`Model.ordered_choice()`](../Model/ordered_choice.md)
- [`Model.query()`](../Model/query.md)
- [`Model.rule()`](../Model/rule.md)
- [`Model.scope()`](../Model/scope.md)
- [`Module.union()`](../Model/union.md)
