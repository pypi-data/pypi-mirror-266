# `relationalai.clients.Snowflake.PrimaryKey`

The `PrimaryKey` class is used to set which columns of a Snowflake table comprise the table's primary key.
Usually, primary key relationships are read automatically when tables are imported.
Use `PrimaryKey` to add any missing relationships.

```python
class relationalai.clients.snowflake.PrimaryKey()
```

## Parameters

None.

## Example

Pass a `PrimaryKey` instance to [`SnowflakeTable.describe()`](./SnowflakeTable/describe.md) to set one or more columns
as the table's primary key:

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

## See Also

[`SnowflakeTable.describe()`](./SnowflakeTable/describe.md)
