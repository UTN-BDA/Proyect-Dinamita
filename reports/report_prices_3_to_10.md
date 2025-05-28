# Informe de Índices para price BETWEEN 3 y 10

## 1. B-tree sin índice
```
Seq Scan on games_game  (cost=0.00..18663.78 rows=40064 width=1155) (actual time=0.083..64.616 rows=40326 loops=1)
  Filter: ((price >= '3'::double precision) AND (price <= '10'::double precision))
  Rows Removed by Filter: 71126
Planning Time: 3.440 ms
Execution Time: 65.694 ms
```
## 2. Creación índice B-tree
```
CREATE INDEX idx_games_game_price ON games_game(price);
```
### Consulta con índice B-tree
```
Bitmap Heap Scan on games_game  (cost=859.07..18452.03 rows=40064 width=1155) (actual time=8.639..98.394 rows=40326 loops=1)
  Recheck Cond: ((price >= '3'::double precision) AND (price <= '10'::double precision))
  Heap Blocks: exact=16001
  ->  Bitmap Index Scan on idx_games_game_price  (cost=0.00..849.06 rows=40064 width=0) (actual time=6.843..6.843 rows=40326 loops=1)
        Index Cond: ((price >= '3'::double precision) AND (price <= '10'::double precision))
Planning Time: 1.275 ms
Execution Time: 100.364 ms
```
## 3. Dimensionamiento B-tree
- Tamaño tabla `games_game`: 133 MB
- Tamaño índice B-tree `idx_games_game_price`: 2472 kB
## 4. Índice Hash
### Creación índice Hash
```
CREATE INDEX idx_games_game_price_hash ON games_game USING HASH (price);
```
### Consulta con índice Hash
```
Seq Scan on games_game  (cost=0.00..18663.78 rows=40064 width=1155) (actual time=0.040..36.012 rows=40326 loops=1)
  Filter: ((price >= '3'::double precision) AND (price <= '10'::double precision))
  Rows Removed by Filter: 71126
Planning Time: 0.645 ms
Execution Time: 37.008 ms
```
## 5. Dimensionamiento Hash
- Tamaño índice Hash `idx_games_game_price_hash`: 5984 kB
## 6. Conclusiones y recomendaciones