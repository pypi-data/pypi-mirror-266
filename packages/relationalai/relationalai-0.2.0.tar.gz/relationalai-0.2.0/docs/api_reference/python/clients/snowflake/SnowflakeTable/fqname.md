# `relationalai.clients.snowflake.SnowflakeTable.fqname()`

```python
relationalai.clients.snowflake.SnowflakeTable.namespace() -> str
```

Returns the [fully-qualified](https://docs.snowflake.com/en/sql-reference/name-resolution) Snowflake table name
as a string of the form `"<db_name>.<schema_name>.<table_name>"`.

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

print(Person.fqname())
# Output:
# 'sandbox.public.people'
```

## See Also

[`SnowflakeTable.namespace()`](./namespace.md)
