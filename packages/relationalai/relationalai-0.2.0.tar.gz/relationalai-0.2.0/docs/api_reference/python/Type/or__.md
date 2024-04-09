# `relationalai.Type.__or__()`

```python
relationalai.Type.__or__(self, __value: Any) -> TypeUnion
```

Types support the `|` operator for expressing the union of two types.

## Returns

A `TypeUnion` object.
`TypeUnion` objects behave just like `Type` objects.

## Example

```python
import relationalai as rai

model = rai.Model("books")

# Create Book, Fiction, NonFiction, Fantasy, and SciFi types.
Book = model.Type("Book")
Fiction = model.Type("Fiction")
NonFiction = model.Type("NonFiction")
Fantasy = model.Type("Fantasy")
SciFi = model.Type("SciFi")

# Add some book instance to the Book type.
with model.rule():
    Book.add(Fiction, Fantasy, name="The Hobbit", author="J.R.R. Tolkien")
    Book.add(Fiction, SciFi, name="Foundation", author="Isaac Asimov")
    Book.add(NonFiction, name="Humble Pi", author="Matt Parker")

# Get the names and authros of all books that are nonfiction or fantasy.
with model.query() as select:
    book = Book(NonFiction | Fantasy)
    response = select(book.name, book.author)

print(response.results)
# Output:
#          name          author
# 0   Humble Pi     Matt Parker
# 1  The Hobbit  J.R.R. Tolkien
```

In English, this query says:
"Select `book.name` and `book.author` where `book` is a `Book` object that is also a
`NonFiction` object or a `Fantasy` object."
