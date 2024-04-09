# `relationalai.Context.results`

A [`Context`](./README.md) object attribute assigned to a
[pandas DataFrame](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html)
containing results selected in a [`model.query()`](../Model/query.md) context.

## Returns

A pandas [`DataFrame`](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html) object.

## Example

Access `.results` after selecting results in a query:

```python
import relationalai as rai

model = rai.Model("people")
Person = model.Type("Person")

with model.rule():
    Person.add(name="Alice", age="31")
    Person.add(name="Alice", age="27")
    Person.add(name="Bob", author="19")

with model.query() as select:
    person = Person()
    response = select(person.name, person.age)

print(response.results)
# Output:
#     name age
# 0  Alice  27
# 1  Alice  31
# 2    Bob  19
```

Calling a [`ContextSelect`](../ContextSelect/README.md) object, like `select` in the preceding query, returns its `Context` object.
In this case, `response` is the `Context` object created by [`model.query()`](../Model/query.md) in the `with` statement.

By default, results are in ascending [lexicographic order](https://en.wikipedia.org/wiki/Lexicographic_order).
In the preceding example, all names beginning with `A` come first, followed by names starting with `B`, and so on.
If two names are the same, such as the two people named `"Alice"`,
the remaining columns are used to determine the sort position of the rows.
In this case, the row for the 27-year-old Alice comes first.

See the [pandas docs](https://pandas.pydata.org/pandas-docs/stable/reference/frame.html)
for details about everything you can do with a DataFrame.

## See Also

[`ContextSelect`](../ContextSelect/README.md) and [`Model.query()`](../Model/query.md).
