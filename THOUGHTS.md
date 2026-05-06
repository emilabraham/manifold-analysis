# Thoughts

## Breakdown by resolution

I ignored all the markets that didn't resolve.
It looks like 49% of markets are resolved to `NO` and 39% resolved to `YES`.
That's already a good sign that just betting `NO` gives you a slight edge.
`CANCEL` means the market was cancelled.
I think I can ignore them.
`MKT` means that the market was auto-resolved because the author didn't resolve it.
It automatically resolves to paying out investors according to the current odds.
I think I can ignore them too.

### Query

```sql
select c.resolution, count(*)
from contracts c
where c.is_resolved = true
group by c.resolution;
```

### Result

| resolution | count(*) |
|------------|----------|
| CANCEL     | 5811     |
| MKT        | 1393     |
| NO         | 33238    |
| YES        | 26781    |
