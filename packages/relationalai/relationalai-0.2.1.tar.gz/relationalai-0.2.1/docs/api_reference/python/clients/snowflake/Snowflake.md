# `relationalai.clients.snowflake.Snowflake`

The `Snowflake` class provides an interface for importing data from a Snowflake database
as objects in a [model](../../Model/README.md).

```python
class relationalai.clients.snowflake.Snowflake(model: Model, auto_import: bool = False)
```

## Parameters

| Name | Type | Description |
| :--- | :--- | :------ |
| `model` | [`Model`](../../Model/README.md) | The model for which the `Snowflake` class is created. |
| `auto_import` | `bool` | Whether or not Snowflake tables referenced from the `Snowflake` class are automatically imported into the model. By default, `auto_import` is `False` and any tables needed in your model should be pre-imported using, for example, the [`rai` CLI](../../../cli/README.md). |

> [!CAUTION]
> The `auto_import` feature is experimental.

## Example

Pass a `Model` object to the `Snowflake` class constructor to create a `Snowflake` instance for your model:

```python
import relationalai as rai
from relationalai.clients.snowflake import Snowflake

model = rai.Model("myModel")

# Get a new Snowflake instance for the model.
sf = Snowflake(model)

# To access a table, use `sf.<db_name>.<schema_name>.<table_name>`.
Person = sf.sandbox.public.people

# Objects from the `Person` table may be used in rules and queries.
# For example, you can augment `Person` objects with an `Adult` type.
Adult = model.Type("Adult")
with model.rule():
    person = Person()
    person.age >= 18
    person.set(Adult)
```

The `Person` object returned by `sf.sandbox.public.people` is a [`SnowflakeTable`](./SnowflakeTable.md) instance.
You can think of a `SnowflakeTable` object as a read-only [`Type`](../../Type/README.md).
Property names, such as `age`, are taken from the columns of the table and are case-insensitive.
See [`SnowflakeTable`](./SnowflakeTable/) for more details.

A table's schema, including primary and foreign key relationships, is automatically read when tables are imported.
If the schema information is missing, or you need to provide additional information,
use the [`SnowflakeTable.describe()`](./SnowflakeTable/describe.md) method:

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

[`PrimaryKey`](./PrimaryKey.md) and [`SnowflakeTable.describe()`](./SnowflakeTable/describe.md)
