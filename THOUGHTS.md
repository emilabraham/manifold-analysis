# Thoughts

## Questions I want answered

### Can I use tags to filter out questions where something always happens? ie. filter out markets about sports games winners

### Should I care about market close date? Is it better to bet on markets that are closing soon?

### How do the following interesting columns impact things? volume, total liquidity, elasticity, prob

### Do I need some sort of semantic analysis on the question?

### Should I bet on markets I've already bet on? Should it be based on probability changes?

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

## Interesting columns

These are some interesting columns that might be relevant or provide insight.

### Query

```sql
select
c.question,
c.volume,
c.total_liquidity,
c.elasticity,
c.pool_yes,
c.pool_no,
c.resolution_probability,
c.p,
c.prob,
c.group_slugs
from contracts c
where c.is_resolved = true
and c.resolution = 'NO';
```

## Tags/Slugs

### empty values

It looks like there are a few that have a `null` or `[]` value.
Almost 4000/33000 of the `NO`.
I think these are safe to ignore.

### Query

```sql
-- A few end up being null or []
select
count(c.group_slugs)
from contracts c
where c.is_resolved = true
and c.resolution = 'NO';
```

### Grouped and Counted by Tag

Here are the top 10 categories and their counts

```
| tag                        | count |
|----------------------------|-------|
| new-years-resolutions-2024 | 5,069 |
| sports-default             | 2,724 |
| destinygg                  | 1,943 |
| politics-default           | 1,880 |
| economics-default          | 1,647 |
| us-politics                | 1,505 |
| soccer                     | 1,387 |
| technology-default         | 1,337 |
| manifold-6748e065087e      | 1,245 |
| stocks                     | 1,157 |
```

There are about `3050` unique tags.
I should filter out the ones that clearly shouldn't be picked up by the bot.

### Query
```sql
SELECT
	je.value AS tag,
	COUNT(*) AS count
FROM
	contracts c,
	json_each(c.group_slugs) je
WHERE
	c.is_resolved = true
	AND c.resolution = 'NO'
	AND c.group_slugs IS NOT NULL
	AND c.group_slugs  != '[]'
GROUP BY
	je.value
ORDER BY
	count DESC;
```

### Filtering out tags

`new-years-resolutions-2024` seems like an outlier.
I think manifold had an event where they encouraged market creation for these.
Then had a resolution party to resolve them all.

I can confidently ignore `sports-default` since something "always happens".

`destinygg` refers to a streamer named [Destiny](https://www.destiny.gg/).
It seems like there are lot of questions that fit so I'll leave it in.

I manually selected a few of the sports related tags that had more than `100` markets.

```
sports-default
soccer
football
nfl
nba
college-football
basketball
premiere-league
2022-fifa-world-cup
motorsports
hockey
nhl
baseball
soccer-friendlies
chess
road-bicycle-racing
mlb
uefa-champions-league
college-basketball
```

I think that should be a good start on filtering.

### Query

```sql
SELECT
    je.value AS tag,
    COUNT(*) AS count
  FROM contracts c, json_each(c.group_slugs) je
  WHERE c.is_resolved = true
    AND c.resolution = 'NO'
    AND c.group_slugs IS NOT NULL
    AND je.value NOT IN (
      'sports-default',
      'soccer',
      'football',
      'nfl',
      'nba',
      'college-football',
      'basketball',
      'premiere-league',
      '2022-fifa-world-cup',
      'motorsports',
      'hockey',
      'nhl',
      'baseball',
      'soccer-friendlies',
      'chess',
      'road-bicycle-racing',
      'mlb',
      'uefa-champions-league',
      'college-basketball'
    )
  GROUP BY je.value
  ORDER BY count DESC;
```

## Resources

### [Market Mechanics](https://news.manifold.markets/p/above-the-fold-market-mechanics)

The simplest example is racehorse betting([parimutuel betting](https://en.wikipedia.org/wiki/Parimutuel_betting)).
No starting liquidity needed.
All the money goes into a pool.
The ratio of cash between each of the options determines the odds.
Final payout is not determined until the pool is closed (right before the race starts).
However, many horse race tracks show odds based on the existing pool ratio should no more bets be accepted after current time.
This differs from fixed-odds betting where the payout is agreed at the time the bet is made.

The mechanism they decided to use is constant-product market maker.
In summary, it allows for adding liquidity (adding more money to the pool without changing the ratio) by creating shares proportionally so that:

```
X * Y = K
```
