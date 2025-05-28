# Informe de Índices para price BETWEEN 3 y 300

## 1. B-tree sin índice
```
Seq Scan on games_game  (cost=0.00..18663.78 rows=61355 width=1155) (actual time=0.065..66.560 rows=61625 loops=1)
  Filter: ((price >= '3'::double precision) AND (price <= '300'::double precision))
  Rows Removed by Filter: 49827
Planning Time: 3.674 ms
Execution Time: 68.106 ms
```
## 2. Creación índice B-tree
```
CREATE INDEX idx_games_game_price ON games_game(price);
```
### Consulta con índice B-tree
```
Seq Scan on games_game  (cost=0.00..18663.78 rows=61355 width=1155) (actual time=0.043..51.100 rows=61625 loops=1)
  Filter: ((price >= '3'::double precision) AND (price <= '300'::double precision))
  Rows Removed by Filter: 49827
Planning Time: 1.829 ms
Execution Time: 52.605 ms
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
Seq Scan on games_game  (cost=0.00..18663.78 rows=61355 width=1155) (actual time=0.034..50.962 rows=61625 loops=1)
  Filter: ((price >= '3'::double precision) AND (price <= '300'::double precision))
  Rows Removed by Filter: 49827
Planning Time: 0.612 ms
Execution Time: 52.476 ms
```
## 5. Dimensionamiento Hash
- Tamaño índice Hash `idx_games_game_price_hash`: 5984 kB
## 6. Conclusiones y recomendaciones