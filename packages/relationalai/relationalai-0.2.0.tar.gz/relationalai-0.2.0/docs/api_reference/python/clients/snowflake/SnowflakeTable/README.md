# `relationalai.clients.Snowflake.SnowflakeTable`

The `SnowflakeTable` class represents an existing table in your Snowflake account.
You create `SnowflakeTable` instances using a [`Snowflake`](../Snowflake.md) object.

```python
class relationalai.clients.snowflake.SnowflakeTable()
```

> [!IMPORTANT]
> You must stream the contents of a Snowflake table to your [model](../../../Model/README.md)
> before you can access the table with RelationalAI.
> Snowflake admins can set up streams using the [SQL library](../../../../sql/README.md)
> or the CLI's [`imports:stream`](../../../../cli/README.md#importsstream) command.

## Parameters

None.

## Methods

- [`SnowflakeTable.describe()`](./describe.md)

## Example

```python
import relationalai as rai
from relationalai.clients.snowflake import Snowflake

model = rai.Model("myModel")

# Get a new Snowflake instance for the model.
sf = Snowflake(model)

# To access a table, use `sf.<db_name>.<schema_name>.<table_name>`.
Person = sf.sandbox.public.people

# `Person` behaves like a read-only `Type`.
# For instance, this query gets the names and ages of all people.
with model.query() as select:
    person = Person()
    response = (person.name, person.age)
```

The `Person` object returned by `sf.sandbox.public.people` is a [`SnowflakeTable`](./SnowflakeTable.md) instance.
The table is presumed to be in [third normal form](https://en.wikipedia.org/wiki/Third_normal_form).

Think of `SnowflakeTable` as a read-only [`Type`](../../Type/call__.md).
Although you may query a `SnowflakeTable` as if it were a `Type` object,
you can't add objects to a table like you can using [`Type.add()`](../../Type/add.md).

Property names, such as `age`, come from the table's column names and are case-insensitive.
For example, if the column in the table is named `AGE` in all caps,
then `person.AGE` and `person.age` both refer to the same column.

Use the [`SnowflakeTable.describe()`](./SnowflakeTable/describe.md) method to describe table columns,
such as which column serves as the [primary key](./PrimaryKey.md):

```python
import relationalai as rai
from relationalai.clients.snowflake import Snowflake, PrimaryKey

model = rai.Model("myModel")
sf = Snowflake(model)

Person = sf.sandbox.public.people
# Set the `id` column as the primary key.
Person.describe(id=PrimaryKey)
```

Multiple primary key columns are supported.
You may also define foreign key relationships.
See [`SnowflakeTable.describe()`](./SnowflakeTable/describe.md) for more details.

## See Also

[`PrimaryKey`](./PrimaryKey.md) and [`Snowflake`](../Snowflake.md)
