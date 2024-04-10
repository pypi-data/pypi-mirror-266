# `relationalai.clients.snowflake.SnowflakeTable.namespace()`

```python
relationalai.clients.snowflake.SnowflakeTable.namespace() -> str
```

Returns the Snowflake namespace of the table as a string of the form `"<db_name>.<schema_name>"`.

## Parameters

None.

## Returns

A `str` object.

## Example

```python
import relationalai as rai
from relationalai.clients.snowflake import Snowflake, PrimaryKey

model = rai.Model("myModel")
sf = Snowflake(model)
Person = sf.sandbox.public.people

print(Person.namespace())
# Output:
# 'sandbox.public'
```

To get the [fully-qualified](https://docs.snowflake.com/en/sql-reference/name-resolution) table name,
use [`.fqname()`](./fqname.md).

## See Also

[`SnowflakeTable.fqname()`](./fqname.md)
