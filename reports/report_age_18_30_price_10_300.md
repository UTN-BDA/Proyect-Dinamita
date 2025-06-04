# Informe de índices: required_age BETWEEN 18 y 30, price BETWEEN 10 y 300

- Tamaño tabla `games_game`: 133 MB

## 1. Sin índice
```sql
Gather  (cost=1000.00..18927.27 rows=65 width=1155) (actual time=2.644..57.647 rows=125 loops=1)
  Workers Planned: 2
  Workers Launched: 2
  ->  Parallel Seq Scan on games_game  (cost=0.00..17920.77 rows=27 width=1155) (actual time=1.200..28.486 rows=42 loops=3)
        Filter: ((required_age >= '18'::double precision) AND (required_age <= '30'::double precision) AND (price >= '10'::double precision) AND (price <= '300'::double precision))
        Rows Removed by Filter: 37109
Planning Time: 2.814 ms
Execution Time: 57.703 ms
```
## 2. Índice B-tree (required_age, price)
```sql
CREATE INDEX idx_games_game_age_price ON games_game(required_age, price);
```
### Consulta con índice B-tree
```sql
Index Scan using idx_games_game_age_price on games_game  (cost=0.42..146.26 rows=65 width=1155) (actual time=0.027..0.757 rows=125 loops=1)
  Index Cond: ((required_age >= '18'::double precision) AND (required_age <= '30'::double precision) AND (price >= '10'::double precision) AND (price <= '300'::double precision))
Planning Time: 1.785 ms
Execution Time: 0.775 ms
```
- Tamaño índice B-tree: 3464 kB

## 3. Índice Hash (required_age, price)
```sql
CREATE INDEX idx_games_game_age_price_hs ON games_game USING HASH (required_age, price);
```
_Índice Hash no soportado o falló: el método de acceso «hash» no soporta índices multicolumna_
