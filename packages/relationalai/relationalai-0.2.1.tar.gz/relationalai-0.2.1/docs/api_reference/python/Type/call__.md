# `relationalai.Type.__call__()`

```python
relationalai.Type.__call__(self, *args, **kwargs) -> Instance
```

Returns an [`Instance`](../Instance/README.md) that produces objects from `Type`.
You must call a type from within a [rule](../Model/rule.md) or [query](../Model/query.md) context.

## Parameters

| Name | Type | Description |
| :--- | :--- | :------ |
| `*args` | `Any` | Any additional types that found objects must have. |
| `*kwargs` | `Any` | Properties and values that found objects must have. |

## Returns

An [`Instance`](../Instance/README.md) object.

## Example

When you call a `Type` object without any arguments it returns an [`Instance`](../Instance/README.md)
that produces every object of that type:

```python
import relationalai as rai

model = rai.Model("books")

# Create Book, Fiction, and NonFiction types.
Book = model.Type("Book")
Fiction = model.Type("Fiction")
NonFiction = model.Type("NonFiction")

# Add some book instance to the Book type.
with model.rule():
    Book.add(Fiction, name="Foundation", author="Isaac Asimov")
    Book.add(NonFiction, name="Humble Pi", author="Matt Parker")

# Get the name of every book.
with model.query() as select:
    book = Book()
    response = select(book.name)

print(response.results)
# Output:
#          name
# 0  Foundation
# 1   Humble Pi
```

In English, this query says:
"Select `book.name` where `book` is a `Book` object."
In logic jargon, `book = Book()` binds the instance `book` to the `Book` collection.

Pass property values as keyword arguments when you call a type to
get an `Instance` that produces objects with those properties:

```python
# Who is the author of Foundation?
with model.query() as select:
    book = Book(name="Foundation")
    response = select(book.author)

print(response.results)
# Output:
#          author
# 0  Isaac Asimov
```

You may pass additional types as positional parameters to produce objects with multiple types:

```python
# What are the names of fiction books written by Isaac Asimov?
with model.query() as select:
    book = Book(Fiction, author="Isaac Asimov")
    response = select(book.name)

print(response.results)
# Output:
#          name
# 0  Foundation
```

If you pass a type only and no properties, the result is the intersection of objects in the types:

```python
with model.query() as select:
    book = Book(NonFiction)
    response = select(book.name, book.author)

print(response.results)
# Output:
#         name       author
# 0  Humble Pi  Matt Parker
```

## See Also

[`Instance`](../Instance/README.md)
