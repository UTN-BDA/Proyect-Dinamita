# Reporte búsqueda por name = 'MosGhost'

## 1. Sin índice B-tree
```
Index Scan using idx_game_name_hash on games_game  (cost=0.00..8.02 rows=1 width=1148) (actual time=0.046..0.047 rows=1 loops=1)
  Index Cond: ((name)::text = 'MosGhost'::text)
Planning Time: 6.168 ms
Execution Time: 0.076 ms
```
## 2. Con índice B-tree
```
Index Scan using idx_game_name_hash on games_game  (cost=0.00..8.02 rows=1 width=1148) (actual time=0.010..0.010 rows=1 loops=1)
  Index Cond: ((name)::text = 'MosGhost'::text)
Planning Time: 1.181 ms
Execution Time: 0.026 ms
```
## 3. Tamaño índice B-tree
- Tabla `games_game`: 133 MB
- Índice `idx_game_name_btree`: 4304 kB
## 4. Índice Hash
```
Index Scan using idx_game_name_hash on games_game  (cost=0.00..8.02 rows=1 width=1148) (actual time=0.011..0.012 rows=1 loops=1)
  Index Cond: ((name)::text = 'MosGhost'::text)
Planning Time: 0.684 ms
Execution Time: 0.027 ms
```
- Índice `idx_game_name_hash`: 4112 kB
## 5. Conclusiones
```
pass
```