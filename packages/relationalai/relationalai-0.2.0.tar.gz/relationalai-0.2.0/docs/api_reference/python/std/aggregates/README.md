<!-- markdownlint-disable MD024 -->

# `relationalai.std.aggregates`

The `relationalai.std.aggregates` namespace contains functions for performing
aggregations, such as [`count()`]() and [`sum()`]() on values produced by [`Producer`](../../Producer/README.md) objects.

To use functions from `relationalai.std.aggregates`, include the following import
at the top of your Python file:

```python
from relationalai.std import aggregates
```

If you would like a shorter name than `aggregates`, you may rename it as `agg`:

```python
from relationalai.std import aggregates as agg
```

## Contents

- [`relationalai.std.aggregates.avg()`](./avg.md)
- [`relationalai.std.aggregates.count()`](./count.md)
- [`relationalai.std.aggregates.max()`](./max.md)
- [`relationalai.std.aggregates.min()`](./min.md)
- [`relationalai.std.aggregates.rank_asc()`](./rank_asc.md)
- [`relationalai.std.aggregates.rank_desc()`](./rank_desc.md)
- [`relationalai.std.aggregates.sum()`](./sum.md)
