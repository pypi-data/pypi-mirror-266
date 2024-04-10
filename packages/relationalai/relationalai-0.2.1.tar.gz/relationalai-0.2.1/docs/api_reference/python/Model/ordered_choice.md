# `relationalai.Model.ordered_choice()`

```python
Model.ordered_choice(dynamic: bool = True) -> Context
```

Creates a [`Context`](../Context/README.md) that applies consecutive `with` blocks in an "if-else" fashion.

## Parameters

| Name | Type | Description |
| :--- | :--- | :------ |
| `dynamic` | `bool` | Whether or not the context is dynamic. Dynamic queries support Python control flow as macros. See [`Context`](../Context/README.md) for more information. |

## Returns

A [`Context`](../Context/README.md) object.

## Example

`Model.ordered_choice()` is a
[context manager](https://docs.python.org/3/glossary.html#term-context-manager)
and should be called in a `with` statement.
It must be called from within a [rule](./rule.md) or [query](./query.md) context:

```python
import relationalai as rai

model = rai.Model("students")
Student = model.Type("Student")

with model.rule():
    Student.add(name="Fred", grade=87)
    Student.add(name="Johnny", grade=65)
    Student.add(name="Mary", grade=98)

# `model.ordered_choice()` is always called in a nested `with` block
# inside of a `model.rule()` or `model.query()` context.
with model.rule():
    student = Student()
    # Set a `letter_grade` property on students whose value
    # depends on their `.grade` property. Note that only `with`
    # statements are allowed inside of a `Model.ordered_choice()` context.
    with model.ordered_choice():
        with student.grade >= 90:
            # A `with` block may contain any valid query builder code.
            student.set(letter_grade="A")
        with student.grade >= 80:
            student.set(letter_grade="B")
        with student.grade >= 70:
            student.set(letter_grade="C")
        with student.grade < 70:
            student.set(letter_grade="F")

# Which students got a B?
with model.query() as select:
    student = Student(letter_grade="B")
    response = select(student.name, student.grade, student.letter_grade)

print(response.results)
# Output:
#    name  grade letter_grade
# 0  Fred     87            B
```

The [`Model.ordered_choice().__enter__()`](../Context/enter__.md) method
returns a [`ContextSelect`](../ContextSelect/README.md) object that you may use to choose objects and set properties
in a query instead of a rule.
For instance, the following example calculates letter grades in a query instead of setting them as object properties:

```python
import relationalai as rai

model = rai.Model("students")
Student = model.Type("Student")

with model.rule():
    Student.add(name="Fred", grade=87)
    Student.add(name="Johnny", grade=65)
    Student.add(name="Mary", grade=98)

# Which students got a B?
with model.query() as select:
    student = Student()
    with model.ordered_choice() as students:
        with student.grade >= 90:
            students.add(student, letter_grade="A")
        with student.grade >= 80:
            students.add(student, letter_grade="B")
        with student.grade >= 70:
            students.add(student, letter_grade="C")
        with student.grade < 70:
            students.add(student, letter_grade="F")

    students.letter_grade == "B"
    response = select(students.name, students.grade, students.letter_grade)

print(response.results)
# Output:
#    name  grade  v
# 0  Fred     87  B
```

Only `with` statements are allowed inside of a `Model.ordered_choice()` context.
Creating [instances](../Instance/README.md) and other [producers](../Producer/README.md) will result in an error:

```python
with model.rule():
    with model.ordered_choice():
        # THIS IS NOT ALLOWED:
        student = Student()

        # ...
```

Think of consecutive `with` statements inside of a `Model.ordered_choice()` context as branches of an `if`-`else` statement.
The preceding example sets a `letter_grade` property on `student` objects,
the value of which depends on the student's `grade` property.
Only values from the first matching `with` statement are set.

Compare that to the same sequence of `with` statements written outside of a `Model.ordered_choice()` context:

```python
with model.rule():
    student = Student()
    with student.grade >= 90:
        student.set(letter_grade="A")
    with student.grade >= 80:
        student.set(letter_grade="B")
    with student.grade >= 70:
        student.set(letter_grade="C")
    with student.grade < 70:
        student.set(letter_grade="F")

# Which students got a B?
with model.query() as select:
    student = Student(letter_grade="B")
    response = select(student.name, student.grade, student.letter_grade)

print(response.results)
# Output:
#    name  grade letter_grade
# 0  Fred     87            B
# 1  Mary     98            B
```

Mary has `.letter_grade` set to `"B"`.
She _also_ has `.letter_grade` set to `"A"` and `"C"` because her grade meets the conditions
in the first three of the four `with` statements.

## See Also

[`Context`](../Context/README.md),
[`ContextSelect`](../ContextSelect/README.md),
and [`Model.union()`](./union.md).
