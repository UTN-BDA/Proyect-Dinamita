# Informe de índices: price BETWEEN 3 y 300

- Tamaño tabla `games_game`: 133 MB
## Sin índice
```sql
Seq Scan on games_game  (cost=0.00..18663.78 rows=61355 width=1155) (actual time=0.076..70.700 rows=61625 loops=1)
  Filter: ((price >= '3'::double precision) AND (price <= '300'::double precision))
  Rows Removed by Filter: 49827
Planning Time: 5.421 ms
Execution Time: 72.230 ms
```

## Índice B-tree
```sql
CREATE INDEX idx_games_game_price ON games_game(price);
```
### Consulta con índice B-tree
```sql
Seq Scan on games_game  (cost=0.00..18663.78 rows=61355 width=1155) (actual time=0.037..57.082 rows=61625 loops=1)
  Filter: ((price >= '3'::double precision) AND (price <= '300'::double precision))
  Rows Removed by Filter: 49827
Planning Time: 2.296 ms
Execution Time: 58.596 ms
```
- Tamaño índice B-tree: 2472 kB

## Índice Hash
```sql
CREATE INDEX idx_games_game_price_hs ON games_game USING HASH (price);
```
### Consulta con índice Hash
```sql
Seq Scan on games_game  (cost=0.00..18663.78 rows=61355 width=1155) (actual time=0.067..50.594 rows=61625 loops=1)
  Filter: ((price >= '3'::double precision) AND (price <= '300'::double precision))
  Rows Removed by Filter: 49827
Planning Time: 2.749 ms
Execution Time: 52.357 ms
```
- Tamaño índice Hash: 5984 kB