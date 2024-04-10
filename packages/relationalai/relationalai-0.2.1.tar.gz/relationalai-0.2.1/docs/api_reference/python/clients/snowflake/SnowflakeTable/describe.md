# `relationalai.clients.snowflake.SnowflakeTable.describe()`

```python
relationalai.clients.snowflake.SnowflakeTable.describe(**kwargs) -> SnowflakeTable
```

Set the primary and foreign key relationships defined in a table.
Usually, this isn't necessary as schema is automatically read when Snowflake tables are imported.
Use `.describe()` to set any missing relationships that aren't defined in Snowflake.

## Parameters

| Name | Type | Description |
| :--- | :--- | :------ |
| `*kwargs` | `PrimaryKey \| Tuple[SnowflakeTable, str]` | Pairs of column names and their primary key and foreign key |

## Returns

The [`SnowflakeTable`](./README.md) object from which `.describe()` was called.

## Example

Use `SnowflakeTable.describe()` to set which columns constitute the [primary key](./PrimaryKey.md):

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
You may also define foreign key relationships:

```python
import relationalai as rai
from relationalai.clients.snowflake import Snowflake

model = rai.Model("myModel")
sf = Snowflake(model)
Person = sf.sandbox.public.people
Address = sf.sandbox.public.address

# Set the `person_id` column of the `Address` table as a foreign key
# referencing the `Person` table. The `"person"` string becomes the
# property name for the related objects.
Address.describe(person_id=(Person, "person"))

# Now use `Address.person` to get the address of the person named "Bob".
with model.query() as select:
    address = Address()
    address.person.name == "Bob"
    response = select(address.street, address.city, address.state)
```

## See Also

[`PrimaryKey`](./PrimaryKey.md) and [`SnowflakeTable`](../SnowflakeTable/README.md)
