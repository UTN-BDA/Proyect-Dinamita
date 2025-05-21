# Informe de Índices para app_id The Apothem have arrived - and they want to play some serious games with Earthlings. Influenced by classic top-down shooters like Sinistar and Bosconian, Shibui Coliseum is a multidirectonally scrolling shoot ‘em up for fans of fast-paced arcade action. Face 100 waves of increasingly deadly Apothem assault craft, spread over 10 vastly different arenas Find a way to disable the Apothem command craft, The Anthracite, which relentlessly chases you for the entire duration of the game Ran out of ammo or simply feel like parading your space suit? Teleport your pilot on to the arena surface and punish your enemies using your trusty peashooter Level up your craft’s weapons systems and enjoy a dapper new paintjob or two

## 1. B-tree sin índice
```
Seq Scan on games_game  (cost=0.00..18385.15 rows=1 width=1155) (actual time=61.240..61.240 rows=0 loops=1)
  Filter: (about_game = 'The Apothem have arrived - and they want to play some serious games with Earthlings. Influenced by classic top-down shooters like Sinistar and Bosconian, Shibui Coliseum is a multidirectonally scrolling shoot ‘em up for fans of fast-paced arcade action. Face 100 waves of increasingly deadly Apothem assault craft, spread over 10 vastly different arenas Find a way to disable the Apothem command craft, The Anthracite, which relentlessly chases you for the entire duration of the game Ran out of ammo or simply feel like parading your space suit? Teleport your pilot on to the arena surface and punish your enemies using your trusty peashooter Level up your craft’s weapons systems and enjoy a dapper new paintjob or two'::text)
  Rows Removed by Filter: 111452
Planning Time: 3.803 ms
Execution Time: 61.272 ms
```
## 2. Creación índice B-tree
```
CREATE INDEX idx_games_game_about_game ON games_game(app_id);
```
### Consulta con índice B-tree
```
Seq Scan on games_game  (cost=0.00..18385.15 rows=1 width=1155) (actual time=48.258..48.258 rows=0 loops=1)
  Filter: (about_game = 'The Apothem have arrived - and they want to play some serious games with Earthlings. Influenced by classic top-down shooters like Sinistar and Bosconian, Shibui Coliseum is a multidirectonally scrolling shoot ‘em up for fans of fast-paced arcade action. Face 100 waves of increasingly deadly Apothem assault craft, spread over 10 vastly different arenas Find a way to disable the Apothem command craft, The Anthracite, which relentlessly chases you for the entire duration of the game Ran out of ammo or simply feel like parading your space suit? Teleport your pilot on to the arena surface and punish your enemies using your trusty peashooter Level up your craft’s weapons systems and enjoy a dapper new paintjob or two'::text)
  Rows Removed by Filter: 111452
Planning Time: 0.988 ms
Execution Time: 48.276 ms
```
## 3. Dimensionamiento B-tree
- Tamaño tabla `games_game`: 133 MB
- Tamaño índice B-tree `idx_games_game_about_game`: 2472 kB
## 4. Índice Hash
### Creación índice Hash
```
CREATE INDEX idx_games_game_about_game_hash ON games_game USING HASH (app_id);
```
### Consulta con índice Hash
```
Seq Scan on games_game  (cost=0.00..18385.15 rows=1 width=1155) (actual time=53.377..53.377 rows=0 loops=1)
  Filter: (about_game = 'The Apothem have arrived - and they want to play some serious games with Earthlings. Influenced by classic top-down shooters like Sinistar and Bosconian, Shibui Coliseum is a multidirectonally scrolling shoot ‘em up for fans of fast-paced arcade action. Face 100 waves of increasingly deadly Apothem assault craft, spread over 10 vastly different arenas Find a way to disable the Apothem command craft, The Anthracite, which relentlessly chases you for the entire duration of the game Ran out of ammo or simply feel like parading your space suit? Teleport your pilot on to the arena surface and punish your enemies using your trusty peashooter Level up your craft’s weapons systems and enjoy a dapper new paintjob or two'::text)
  Rows Removed by Filter: 111452
Planning Time: 0.632 ms
Execution Time: 53.396 ms
```
## 5. Dimensionamiento Hash
- Tamaño índice Hash `idx_games_game_about_game_hash`: 4112 kB
## 6. Conclusiones y recomendaciones