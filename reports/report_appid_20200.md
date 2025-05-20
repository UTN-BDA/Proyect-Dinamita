# Informe de Índices para app_id 20200

## 1. B-tree sin índice

```
Index Scan using idx_games_game_app_id_hash on games_game  (cost=0.00..8.02 rows=1 width=1148) (actual time=0.031..0.031 rows=1 loops=1)
  Index Cond: ((app_id)::text = '20200'::text)
Planning Time: 2.056 ms
Execution Time: 0.049 ms
```

## 2. Creación índice B-tree

```
CREATE INDEX idx_games_game_app_id ON games_game(app_id);
```

### Consulta con índice B-tree

```
Index Scan using idx_games_game_app_id_hash on games_game  (cost=0.00..8.02 rows=1 width=1148) (actual time=0.008..0.008 rows=1 loops=1)
  Index Cond: ((app_id)::text = '20200'::text)
Planning Time: 0.589 ms
Execution Time: 0.021 ms
```

## 3. Dimensionamiento B-tree

- Tamaño tabla `games_game`: 133 MB
- Tamaño índice B-tree `idx_games_game_app_id`: 2472 kB

## 4. Índice Hash

### Creación índice Hash

```
CREATE INDEX idx_games_game_app_id_hash ON games_game USING HASH (app_id);
```

### Consulta con índice Hash

```
Index Scan using idx_games_game_app_id_hash on games_game  (cost=0.00..8.02 rows=1 width=1148) (actual time=0.008..0.009 rows=1 loops=1)
  Index Cond: ((app_id)::text = '20200'::text)
Planning Time: 0.547 ms
Execution Time: 0.019 ms
```

## 5. Dimensionamiento Hash

- Tamaño índice Hash `idx_games_game_app_id_hash`: 4112 kB

## 6. Conclusiones y recomendaciones

### 6.1. Rendimiento

- Sin índice, el Planning Time fue de 2.056 ms y el Execution Time de 0.049 ms.
- Con B‑tree, el Planning Time se redujo a 0.589 ms y el Execution Time a 0.021 ms.
- Con Hash, el Planning Time bajó aún más a 0.547 ms y el Execution Time a 0.019 ms.

Ambos índices aceleran bastante la fase de planificación, hasta casi un cuarto del tiempo original y la ejecución hasta casi la mitad, siendo el Hash ligeramente más rápido en este caso puntual.

### 6.2. Almacenamiento

- La tabla ocupa 133 MB.
  - El índice B‑tree aumentara el tamaño en 2.4 MB aproximadamente.
  - El índice Hash ocupa aproximadamente 4.1 MB, casi el doble que el B‑tree.

### 6.3. Recomendaciones

- El índice B-tree es un buen equilibrio entre espacio y latencia, habria que considerar que tanto peso tiene la diferencia de casi el doble de lo que ocupa Hash.
- Si las consultas a traves de app_id son muy frecuentes se podria considerar el uso de Hash, a pesar del espacio que ocupe.
- En este caso si mejorar significativamente el tiempo de consultas, se recomendaria optar por uno de los dos tipos de índices si o si.
