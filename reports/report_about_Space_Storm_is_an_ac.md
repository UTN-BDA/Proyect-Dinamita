# Reporte búsqueda por about_game = 'Space Storm is an action-packed 2D game in which you control a futuristic spaceship to fight against enemy fleets...'

## 1. Sin índice B-tree
```
Index Scan using idx_about_game_hash on games_game  (cost=0.00..8.02 rows=1 width=1148) (actual time=0.029..0.030 rows=0 loops=1)
  Index Cond: (about_game = 'Space Storm is an action-packed 2D game in which you control a futuristic spaceship to fight against enemy fleets...'::text)
Planning Time: 3.551 ms
Execution Time: 0.070 ms
```
_Error al crear el índice B-tree: fila de índice requiere 8560 bytes, tamaño máximo es 8191
CONTEXT:  ayudante paralelo_
## 4. Índice Hash
```
Index Scan using idx_game_about_hash on games_game  (cost=0.00..8.02 rows=1 width=1148) (actual time=0.024..0.024 rows=0 loops=1)
  Index Cond: (about_game = 'Space Storm is an action-packed 2D game in which you control a futuristic spaceship to fight against enemy fleets...'::text)
Planning Time: 1.515 ms
Execution Time: 0.040 ms
```
- Índice `idx_game_about_hash`: 4240 kB
## 5. Conclusiones
```
pass
```