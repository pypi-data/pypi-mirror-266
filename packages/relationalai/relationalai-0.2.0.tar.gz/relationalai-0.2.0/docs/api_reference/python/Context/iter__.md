# `relationalai.Context.__iter__()`

```python
relationalai.Context.__iter__() --> Iterator
```

Returns an iterator over rows of [`Context.results`](./results.md) that is equivalent to:

```python
context.results.itertuples(index=False)`
```

See [`DataFrame.itertuples()`](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.itertuples.html)
for more information.

## Returns

A Python [iterator](https://docs.python.org/3/glossary.html#term-iterator).

## Example

```python
import relationalai as rai

model = rai.Model("people")
Person = model.Type("Person")

with model.rule():
    Person.add(name="Bonnie")
    Person.add(name="Clyde")

with model.query() as select:
    person = Person()
    response = select(person.name)

for i, row in enumerate(response, start=1):
    print(f"Person {i} is named {row.name}.")
# Output:
# Person 1 is named Bonnie.
# Person 2 is named Clyde.
```

## See Also

[`Context.results`](results.md)
