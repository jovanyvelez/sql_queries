# Cheatsheet SQL — CS50 SQL (adaptación a PostgreSQL)

> Referencia rápida de sintaxis SQL + **soluciones de todas las prácticas** del curso.
> Este archivo es standalone (no forma parte de la app web). Generado con `python generar_cheatsheet.py`.

## Tabla de contenidos

1. [Referencia SQL](#referencia-sql)
2. [Soluciones de todas las prácticas](#soluciones-de-todas-las-prácticas)
   - [Clase 0 — Consultas](#clase-0--consultas)
   - [Clase 1 — Relaciones](#clase-1--relaciones)
   - [Problem Set — DESE](#problem-set--dese)
   - [Problem Set — Moneyball](#problem-set--moneyball)
   - [Problem Set — Packages, Please](#problem-set--packages-please)

---

## Referencia SQL

### Consultas básicas

| Concepto | Sintaxis | Ejemplo | Nota |
|---|---|---|---|
| **SELECT** | `SELECT col1, col2 FROM tabla` | `SELECT titulo, autor FROM libros` | Elige columnas. SELECT * trae todas. |
| **LIMIT** | `SELECT ... LIMIT n` | `SELECT * FROM libros LIMIT 10` | Máximo n filas. Útil para explorar. |
| **DISTINCT** | `SELECT DISTINCT col FROM tabla` | `SELECT DISTINCT editorial_id FROM libros` | Elimina duplicados. |
| **ORDER BY** | `ORDER BY col [ASC\|DESC]` | `SELECT * FROM libros ORDER BY titulo ASC` | Ordena. ASC ascendente (default), DESC descendente. Varios cols separados por coma. |
| **AS (alias)** | `SELECT col AS alias` | `SELECT AVG(puntuacion) AS "promedio"` | Renombra columnas. Con espacios usa comillas dobles. |

### Filtrado (WHERE)

| Concepto | Sintaxis | Ejemplo | Nota |
|---|---|---|---|
| **WHERE** | `WHERE condicion` | `SELECT * FROM libros WHERE ano > 2010` | Filtra filas que cumplen la condición. |
| **Operadores** | `=, !=, <>, <, >, <=, >=` | `WHERE puntuacion >= 4` | != y <> son equivalentes (distinto). |
| **AND / OR / NOT** | `WHERE c1 AND (c2 OR c3)` | `WHERE ano > 2000 AND editorial_id = 3` | Combina condiciones. Usa paréntesis para agrupar. |
| **IS NULL** | `WHERE col IS NULL` | `SELECT * FROM libros WHERE autor IS NULL` | Detecta valores ausentes. IS NOT NULL para lo contrario. |
| **IN** | `WHERE col IN (v1, v2, ...)` | `WHERE editorial_id IN (1, 2, 3)` | Equivalente a varios OR. Acepta subconsultas. |
| **BETWEEN** | `WHERE col BETWEEN a AND b` | `WHERE ano BETWEEN 2000 AND 2010` | Incluye los extremos. Equivalente a >= a AND <= b. |
| **LIKE / ILIKE** | `WHERE col LIKE 'patrón'` | `WHERE titulo LIKE 'El%'` | % = cualquier secuencia, _ = un carácter. ILIKE no distingue mayúsculas. |

### Funciones de agregación

| Concepto | Sintaxis | Ejemplo | Nota |
|---|---|---|---|
| **COUNT** | `COUNT(*) o COUNT(col)` | `SELECT COUNT(*) FROM libros` | Cuenta filas. COUNT(col) ignora NULLs. |
| **AVG / SUM** | `AVG(col) / SUM(col)` | `SELECT AVG(puntuacion) FROM puntuaciones` | Promedio y suma. Ignoran NULLs. |
| **MIN / MAX** | `MIN(col) / MAX(col)` | `SELECT MIN(ano), MAX(ano) FROM libros` | Mínimo y máximo. |
| **ROUND** | `ROUND(numero, decimales)` | `ROUND(AVG(puntuacion)::numeric, 2)` | Redondea a n decimales. En PostgreSQL castea con ::numeric si hace falta. |
| **GROUP BY** | `SELECT col, AGG(col2) ... GROUP BY col` | `SELECT editorial_id, COUNT(*) FROM libros GROUP BY editorial_id` | Agrupa filas por col y aplica agregación a cada grupo. |
| **HAVING** | `GROUP BY col HAVING AGG(col2) > n` | `GROUP BY libro_id HAVING COUNT(*) > 100` | Como WHERE pero para agregaciones. Va después de GROUP BY. |

### JOIN (relacionar tablas)

| Concepto | Sintaxis | Ejemplo | Nota |
|---|---|---|---|
| **INNER JOIN** | `SELECT ... FROM a JOIN b ON a.id = b.a_id` | `SELECT l.titulo, e.editorial FROM libros l JOIN editoriales e ON l.editorial_id = e.id` | Solo filas que coinciden en ambas tablas. |
| **LEFT JOIN** | `FROM a LEFT JOIN b ON a.id = b.a_id` | `SELECT lm.nombre, m.distancia FROM leones_marinos lm LEFT JOIN migraciones m ON lm.id = m.id` | Todas las filas de la izquierda. Si no hay coincidencia, NULLs a la derecha. |
| **RIGHT JOIN** | `FROM a RIGHT JOIN b ON a.id = b.a_id` | `SELECT lm.nombre, m.distancia FROM leones_marinos lm RIGHT JOIN migraciones m ON lm.id = m.id` | Todas las filas de la derecha. |
| **FULL JOIN** | `FROM a FULL JOIN b ON a.id = b.a_id` | `SELECT lm.nombre, m.distancia FROM leones_marinos lm FULL JOIN migraciones m ON lm.id = m.id` | Todas las filas de ambas tablas (UNION de LEFT y RIGHT). |
| **NATURAL JOIN** | `FROM a NATURAL JOIN b` | `SELECT * FROM leones_marinos NATURAL JOIN migraciones` | JOIN automático por columnas con el mismo nombre. Ojo: puede sorprender. |
| **Múltiples JOIN** | `FROM a JOIN b ON ... JOIN c ON ...` | `FROM libros l JOIN autoria au ON l.id=au.libro_id JOIN autores a ON a.id=au.autor_id` | Encadena JOINs. Cada uno con su ON. |

### Subconsultas

| Concepto | Sintaxis | Ejemplo | Nota |
|---|---|---|---|
| **Subconsulta escalar** | `WHERE col = (SELECT ... )` | `SELECT titulo FROM libros WHERE editorial_id = (SELECT id FROM editoriales WHERE editorial = 'Fitzcarraldo Editions')` | Devuelve un solo valor. Va entre paréntesis. |
| **IN con subconsulta** | `WHERE col IN (SELECT ...)` | `SELECT titulo FROM libros WHERE id IN (SELECT libro_id FROM autoria WHERE autor_id = 5)` | Subconsulta que devuelve una columna. |
| **Subconsulta en HAVING** | `HAVING AGG(col) > (SELECT AVG(col) FROM ...)` | `HAVING AVG(puntuacion) > (SELECT AVG(puntuacion) FROM puntuaciones)` | Compara contra un promedio global u otro agregado. |
| **CTE (WITH)** | `WITH nombre AS (SELECT ...) SELECT ... FROM nombre` | `WITH top10 AS (SELECT ... LIMIT 10) SELECT * FROM top10` | Subconsulta con nombre. Útil para reusar o para legibilidad. |

### Conjuntos (UNION / INTERSECT / EXCEPT)

| Concepto | Sintaxis | Ejemplo | Nota |
|---|---|---|---|
| **UNION** | `SELECT ... UNION SELECT ...` | `SELECT nombre FROM autores UNION SELECT nombre FROM traductores` | Combina resultados, elimina duplicados. UNION ALL los conserva. |
| **INTERSECT** | `SELECT ... INTERSECT SELECT ...` | `SELECT nombre FROM autores INTERSECT SELECT nombre FROM traductores` | Filas que están en AMBOS resultados. |
| **EXCEPT** | `SELECT ... EXCEPT SELECT ...` | `SELECT nombre FROM traductores EXCEPT SELECT nombre FROM autores` | Filas del primero que NO están en el segundo. |

---

## Soluciones de todas las prácticas

> **Antes de mirar:** intentá resolver cada ejercicio por tu cuenta durante al menos 5–10 minutos. La práctica activa genera más aprendizaje que leer soluciones pasivamente.

### Clase 0 — Consultas
*SELECT, WHERE, LIKE, ORDER BY, NULL y funciones de agregación.*  
Esquema PostgreSQL: `public`

#### 1. Explora la tabla `basico`
> Escribe una consulta que muestre todas las columnas de todos los libros en la tabla lista_larga. Muestra solo los primeros 5 resultados.

```sql
SELECT * FROM lista_larga LIMIT 5
```

#### 2. Titulos solamente `basico`
> Muestra unicamente la columna titulo de la tabla lista_larga. Limita a los primeros 10 resultados.

```sql
SELECT titulo FROM lista_larga LIMIT 10
```

#### 3. Titulo y autor `basico`
> Muestra las columnas titulo y autor de la tabla lista_larga. Ordena los resultados alfabeticamente por titulo.

```sql
SELECT titulo, autor FROM lista_larga ORDER BY titulo
```

#### 4. Libros del 2023 `basico`
> Encuentra todos los libros que fueron publicados en el anio 2023. Muestra el titulo y el autor.

```sql
SELECT titulo, autor FROM lista_larga WHERE anio = 2023
```

#### 5. Libros que no son tapa dura `basico`
> Muestra el titulo y el formato de los libros que NO son 'hardcover'. Muestra solo 10 resultados.

```sql
SELECT titulo, formato FROM lista_larga WHERE formato != 'hardcover' LIMIT 10
```

#### 6. Los mejores libros `basico`
> Encuentra los 10 libros mejor valorados. Muestra el titulo y la puntuacion, ordenados de mayor a menor puntuacion.

```sql
SELECT titulo, puntuacion FROM lista_larga ORDER BY puntuacion DESC LIMIT 10
```

#### 7. Los peores libros `basico`
> Encuentra los 10 libros con peor puntuacion. Muestra el titulo y la puntuacion, ordenados de menor a mayor.

```sql
SELECT titulo, puntuacion FROM lista_larga ORDER BY puntuacion LIMIT 10
```

#### 8. Libros con 'The' en el titulo `intermedio`
> Encuentra todos los libros cuyo titulo comienza con la palabra 'The'. Usa LIKE para esta busqueda.

```sql
SELECT titulo FROM lista_larga WHERE titulo LIKE 'The %'
```

#### 9. Busqueda por palabra clave `intermedio`
> Encuentra todos los libros que contengan la palabra 'Love' en su titulo, sin importar mayusculas o minusculas.

```sql
SELECT titulo FROM lista_larga WHERE titulo ILIKE '%Love%'
```

#### 10. Rango de anios `intermedio`
> Muestra el titulo, autor y anio de los libros publicados entre 2020 y 2022 (inclusive). Ordena por anio.

```sql
SELECT titulo, autor, anio FROM lista_larga WHERE anio BETWEEN 2020 AND 2022 ORDER BY anio
```

#### 11. Libros sin traductor `intermedio`
> Encuentra los libros que NO tienen traductor registrado. Muestra solo el titulo.

```sql
SELECT titulo FROM lista_larga WHERE traductor IS NULL
```

#### 12. Tapa dura en 2022 o 2023 `intermedio`
> Muestra el titulo, formato y anio de los libros que sean 'hardcover' Y publicados en 2022 O 2023. Combina AND y OR con parentesis.

```sql
SELECT titulo, formato, anio FROM lista_larga WHERE formato = 'hardcover' AND (anio = 2022 OR anio = 2023)
```

#### 13. Libros cortos bien valorados `intermedio`
> Encuentra libros con menos de 200 paginas y puntuacion mayor a 4.0. Muestra titulo, paginas y puntuacion.

```sql
SELECT titulo, paginas, puntuacion FROM lista_larga WHERE paginas < 200 AND puntuacion > 4.0
```

#### 14. Libros con formato especifico `intermedio`
> Muestra los libros que NO son 'paperback' NI 'hardcover'. Muestra el titulo y el formato.

```sql
SELECT titulo, formato FROM lista_larga WHERE formato NOT IN ('paperback', 'hardcover')
```

#### 15. Titulos de 4 letras `intermedio`
> Encuentra libros cuyo titulo tenga exactamente 4 caracteres usando el comodin _ de LIKE. Busca en toda la tabla.

```sql
SELECT titulo FROM lista_larga WHERE titulo LIKE '____'
```

#### 16. Puntuacion promedio `avanzado`
> Calcula la puntuacion promedio de todos los libros en lista_larga. Redondea a 2 decimales.

```sql
SELECT ROUND(AVG(puntuacion)::numeric, 2) AS puntuacion_promedio FROM lista_larga
```

#### 17. Editoriales distintas `avanzado`
> ¿Cuantas editoriales diferentes hay en la tabla lista_larga? Usa COUNT y DISTINCT.

```sql
SELECT COUNT(DISTINCT editorial) AS total_editoriales FROM lista_larga
```

#### 18. Estadisticas de puntuacion `avanzado`
> Muestra en una sola consulta: la puntuacion maxima, la minima y la suma total de votos de todos los libros.

```sql
SELECT MAX(puntuacion) AS maxima, MIN(puntuacion) AS minima, SUM(votos) AS total_votos FROM lista_larga
```

#### 19. Libros mejor valorados que el promedio `avanzado`
> Muestra el titulo y la puntuacion de los libros cuya puntuacion sea mayor que la puntuacion promedio de todos los libros. Ordena de mayor a menor puntuacion. (Pista: usa una subconsulta).

```sql
SELECT titulo, puntuacion FROM lista_larga WHERE puntuacion > (SELECT AVG(puntuacion) FROM lista_larga) ORDER BY puntuacion DESC
```

#### 20. Top 5 con mas votos `avanzado`
> Muestra los 5 libros con mas votos. Incluye titulo, puntuacion y votos. Ordena por votos descendente.

```sql
SELECT titulo, puntuacion, votos FROM lista_larga ORDER BY votos DESC LIMIT 5
```

#### 21. Editoriales con mejor promedio `avanzado`
> Para las editoriales que tienen al menos 2 libros, calcula la puntuacion promedio. Muestra la editorial y su promedio redondeado a 2 decimales. Ordena de mayor a menor promedio. (Pista: GROUP BY con HAVING).

```sql
SELECT editorial, ROUND(AVG(puntuacion)::numeric, 2) AS promedio FROM lista_larga GROUP BY editorial HAVING COUNT(*) >= 2 ORDER BY promedio DESC
```

#### 22. Conteo por formato `avanzado`
> ¿Cuantos libros hay de cada formato? Agrupa por formato, cuenta los libros y ordena por cantidad descendente.

```sql
SELECT formato, COUNT(*) AS cantidad FROM lista_larga GROUP BY formato ORDER BY cantidad DESC
```

#### 23. Libros populares con buenas criticas `avanzado`
> Encuentra libros con mas de 10000 votos y puntuacion superior a 4.0. Muestra titulo, puntuacion y votos, ordenados por puntuacion descendente.

```sql
SELECT titulo, puntuacion, votos FROM lista_larga WHERE votos > 10000 AND puntuacion > 4.0 ORDER BY puntuacion DESC
```

#### 24. Editorial con mayor puntuacion maxima `avanzado`
> ¿Cual es la editorial cuyo libro tiene la mayor puntuacion individual? Muestra la editorial y la puntuacion maxima. (Pista: ORDER BY + LIMIT).

```sql
SELECT editorial, puntuacion FROM lista_larga ORDER BY puntuacion DESC LIMIT 1
```

#### 25. Anio con mejor promedio `avanzado`
> Calcula la puntuacion promedio por anio. Muestra anio y promedio redondeado a 2 decimales, ordenado del mejor promedio al peor. (Pista: GROUP BY anio).

```sql
SELECT anio, ROUND(AVG(puntuacion)::numeric, 2) AS promedio FROM lista_larga GROUP BY anio ORDER BY promedio DESC
```

#### 26. Usando NOT en vez de != `basico`
> Muestra el titulo y formato de los libros que NO son 'hardcover', pero usando la palabra clave NOT en lugar de !=.

```sql
SELECT titulo, formato FROM lista_larga WHERE NOT formato = 'hardcover'
```

#### 27. Operador <> `basico`
> Muestra el titulo y formato de los libros que NO son 'paperback', usando el operador <>.

```sql
SELECT titulo, formato FROM lista_larga WHERE formato <> 'paperback'
```

#### 28. Titulos que terminan con vocal `basico`
> Encuentra los libros cuyo titulo termina con la letra 'a'. Usa el comodin % al inicio del patron LIKE.

```sql
SELECT titulo FROM lista_larga WHERE titulo LIKE '%a'
```

#### 29. Dos anios especificos con OR `basico`
> Muestra el titulo y anio de los libros publicados en 2018 o en 2023. Usa OR sin parentesis.

```sql
SELECT titulo, anio FROM lista_larga WHERE anio = 2018 OR anio = 2023 ORDER BY anio
```

#### 30. Tres condiciones con AND `intermedio`
> Encuentra libros con mas de 200 paginas, menos de 500 paginas, y puntuacion mayor a 3.5. Muestra titulo, paginas y puntuacion.

```sql
SELECT titulo, paginas, puntuacion FROM lista_larga WHERE paginas > 200 AND paginas < 500 AND puntuacion > 3.5 ORDER BY puntuacion DESC
```

#### 31. Fuera de rango con NOT BETWEEN `intermedio`
> Muestra el titulo y anio de los libros publicados FUERA del periodo 2020-2022. Usa NOT BETWEEN.

```sql
SELECT titulo, anio FROM lista_larga WHERE anio NOT BETWEEN 2020 AND 2022 ORDER BY anio
```

#### 32. Orden mixto ASC y DESC `intermedio`
> Muestra titulo, anio y puntuacion de todos los libros. Ordena por anio descendente, y dentro del mismo anio por puntuacion ascendente.

```sql
SELECT titulo, anio, puntuacion FROM lista_larga ORDER BY anio DESC, puntuacion ASC
```

#### 33. MAX y MIN en texto `avanzado`
> ¿Cual es el primer y ultimo titulo alfabeticamente en la base de datos? Usa MIN y MAX sobre la columna titulo.

```sql
SELECT MIN(titulo) AS primer_titulo, MAX(titulo) AS ultimo_titulo FROM lista_larga
```

#### 34. Suma de votos por formato `avanzado`
> Calcula la suma total de votos para los libros en formato 'paperback' y por separado para los 'hardcover'. Muestra el formato y su suma de votos. Usa GROUP BY.

```sql
SELECT formato, SUM(votos) AS total_votos FROM lista_larga WHERE formato IN ('paperback', 'hardcover') GROUP BY formato ORDER BY total_votos DESC
```

#### 35. Libros excelentes con pocas paginas `avanzado`
> ¿Cuantos libros hay con puntuacion mayor a 4.0 y menos de 250 paginas? Muestra el conteo con un alias descriptivo.

```sql
SELECT COUNT(*) AS libros_excelentes_cortos FROM lista_larga WHERE puntuacion > 4.0 AND paginas < 250
```

### Clase 1 — Relaciones
*JOIN, subconsultas, INTERSECT, UNION, EXCEPT y GROUP BY.*  
Esquema PostgreSQL: `public`

#### 1. Libros con su editorial `basico`
> Muestra el titulo de cada libro junto con el nombre de su editorial. Usa JOIN entre libros y editoriales.

```sql
SELECT l.titulo, e.editorial FROM libros l JOIN editoriales e ON l.editorial_id = e.id
```

#### 2. Leones marinos y sus migraciones `basico`
> Combina las tablas leones_marinos y migraciones para mostrar el nombre, la especie, la distancia y los dias de migracion de cada leon marino. Usa JOIN ... ON.

```sql
SELECT lm.nombre, lm.especie, m.distancia, m.dias FROM leones_marinos lm JOIN migraciones m ON lm.id = m.id
```

#### 3. Autores con sus libros `basico`
> Muestra cada autor junto con los titulos de los libros que ha escrito. Necesitas unir tres tablas: autores, autoria y libros.

```sql
SELECT a.nombre, l.titulo FROM autores a JOIN autoria au ON a.id = au.autor_id JOIN libros l ON l.id = au.libro_id ORDER BY a.nombre
```

#### 4. Libros de Fitzcarraldo Editions `basico`
> Usa una subconsulta para encontrar todos los libros publicados por 'Fitzcarraldo Editions'. Muestra solo el titulo.

```sql
SELECT titulo FROM libros WHERE editorial_id = (SELECT id FROM editoriales WHERE editorial = 'Fitzcarraldo Editions')
```

#### 5. Puntuacion promedio de un libro `basico`
> Calcula la puntuacion promedio del libro titulado 'Flights'. Usa una subconsulta para encontrar el libro_id. Redondea a 2 decimales.

```sql
SELECT ROUND(AVG(puntuacion)::numeric, 2) AS promedio FROM puntuaciones WHERE libro_id = (SELECT id FROM libros WHERE titulo = 'Flights')
```

#### 6. Todos los leones marinos `basico`
> Muestra TODOS los leones marinos, incluso si no tienen datos de migracion. Usa LEFT JOIN.

```sql
SELECT lm.nombre, lm.especie, m.distancia, m.dias FROM leones_marinos lm LEFT JOIN migraciones m ON lm.id = m.id
```

#### 7. Union natural `basico`
> Une las tablas leones_marinos y migraciones usando NATURAL JOIN. ¿Que diferencia observas respecto al INNER JOIN?

```sql
SELECT * FROM leones_marinos NATURAL JOIN migraciones
```

#### 8. Libros de Fernanda Melchor `intermedio`
> Encuentra todos los libros escritos por Fernanda Melchor. Usa IN porque un autor puede tener varios libros.

```sql
SELECT titulo FROM libros WHERE id IN (SELECT libro_id FROM autoria WHERE autor_id = (SELECT id FROM autores WHERE nombre = 'Fernanda Melchor'))
```

#### 9. Autores que son traductores `intermedio`
> Encuentra las personas que son tanto autoras como traductoras. Usa INTERSECT entre las tablas autores y traductores.

```sql
SELECT nombre FROM autores INTERSECT SELECT nombre FROM traductores
```

#### 10. Todos los nombres `intermedio`
> Muestra una lista unica de todas las personas (autores y traductores) sin duplicados. Usa UNION.

```sql
SELECT nombre FROM autores UNION SELECT nombre FROM traductores
```

#### 11. Solo traductores `intermedio`
> Encuentra las personas que son traductoras pero NO autoras. Usa EXCEPT.

```sql
SELECT nombre FROM traductores EXCEPT SELECT nombre FROM autores
```

#### 12. Puntuacion promedio por libro `intermedio`
> Calcula la puntuacion promedio de cada libro. Muestra el libro_id y el promedio redondeado a 2 decimales. Ordena de mayor a menor promedio. Usa GROUP BY.

```sql
SELECT libro_id, ROUND(AVG(puntuacion)::numeric, 2) AS promedio FROM puntuaciones GROUP BY libro_id ORDER BY promedio DESC
```

#### 13. Cantidad de puntuaciones por libro `intermedio`
> ¿Cuantas puntuaciones ha recibido cada libro? Muestra el libro_id y el conteo. Ordena por cantidad descendente.

```sql
SELECT libro_id, COUNT(*) AS total FROM puntuaciones GROUP BY libro_id ORDER BY total DESC
```

#### 14. Libros con muchos votos `intermedio`
> Muestra los libros que tienen mas de 1000 puntuaciones. Incluye libro_id y el total. Usa GROUP BY con HAVING.

```sql
SELECT libro_id, COUNT(*) AS total FROM puntuaciones GROUP BY libro_id HAVING COUNT(*) > 1000 ORDER BY total DESC
```

#### 15. Colaboracion entre traductores `intermedio`
> Encuentra los libros que han sido traducidos TANTO por Sophie Hughes COMO por Margaret Jull Costa. Usa INTERSECT con dos subconsultas sobre la tabla traduccion.

```sql
SELECT libro_id FROM traduccion WHERE traductor_id = (SELECT id FROM traductores WHERE nombre = 'Sophie Hughes') INTERSECT SELECT libro_id FROM traduccion WHERE traductor_id = (SELECT id FROM traductores WHERE nombre = 'Margaret Jull Costa')
```

#### 16. Autor de Flights `avanzado`
> Encuentra el nombre del autor que escribio el libro 'Flights'. Necesitas una subconsulta de 3 niveles: libros → autoria → autores.

```sql
SELECT nombre FROM autores WHERE id = (SELECT autor_id FROM autoria WHERE libro_id = (SELECT id FROM libros WHERE titulo = 'Flights'))
```

#### 17. Editorial con mas libros `avanzado`
> ¿Que editorial tiene mas libros en la base de datos? Muestra el nombre de la editorial y el conteo. Ordena descendente y limita a 1. Usa JOIN + GROUP BY.

```sql
SELECT e.editorial, COUNT(l.id) AS total FROM editoriales e JOIN libros l ON e.id = l.editorial_id GROUP BY e.editorial ORDER BY total DESC LIMIT 1
```

#### 18. Libros con mejor promedio (minimo 100 votos) `avanzado`
> Muestra el titulo y la puntuacion promedio de los libros que tienen al menos 100 puntuaciones. Une puntuaciones con libros, agrupa, filtra con HAVING y ordena por promedio descendente. Redondea a 2 decimales.

```sql
SELECT l.titulo, ROUND(AVG(p.puntuacion)::numeric, 2) AS promedio FROM libros l JOIN puntuaciones p ON l.id = p.libro_id GROUP BY l.id, l.titulo HAVING COUNT(*) >= 100 ORDER BY promedio DESC
```

#### 19. Profesion de cada persona `avanzado`
> Crea una consulta que muestre cada persona con su profesion ('autor' o 'traductor'). Personas que son ambas deben aparecer en ambas listas. Usa UNION con SELECT de constante.

```sql
SELECT 'autor' AS profesion, nombre FROM autores UNION SELECT 'traductor' AS profesion, nombre FROM traductores ORDER BY nombre
```

#### 20. Libros, autores y puntuacion en una consulta `avanzado`
> Para cada libro, muestra su titulo, el nombre de su autor, y su puntuacion promedio redondeada a 2 decimales. Ordena por puntuacion descendente. Necesitas unir 4 tablas: libros, autoria, autores y puntuaciones.

```sql
SELECT l.titulo, a.nombre AS autor, ROUND(AVG(p.puntuacion)::numeric, 2) AS promedio FROM libros l JOIN autoria au ON l.id = au.libro_id JOIN autores a ON a.id = au.autor_id LEFT JOIN puntuaciones p ON l.id = p.libro_id GROUP BY l.id, l.titulo, a.nombre ORDER BY promedio DESC NULLS LAST
```

#### 21. El leon marino mas viajero `avanzado`
> Encuentra el leon marino que ha recorrido la mayor distancia total en sus migraciones. Muestra el nombre y la suma de distancias. Usa JOIN + GROUP BY + ORDER BY + LIMIT.

```sql
SELECT lm.nombre, SUM(m.distancia) AS distancia_total FROM leones_marinos lm JOIN migraciones m ON lm.id = m.id GROUP BY lm.id, lm.nombre ORDER BY distancia_total DESC LIMIT 1
```

#### 22. Libros de editoriales con puntuacion alta `avanzado`
> Encuentra los libros cuyas editoriales tienen una puntuacion promedio mayor a 3.8. Muestra el titulo del libro y la editorial. (Pista: filtra editoriales con subconsulta en HAVING).

```sql
SELECT l.titulo, e.editorial FROM libros l JOIN editoriales e ON l.editorial_id = e.id WHERE e.id IN (SELECT e2.id FROM editoriales e2 JOIN libros l2 ON e2.id = l2.editorial_id JOIN puntuaciones p ON l2.id = p.libro_id GROUP BY e2.id HAVING AVG(p.puntuacion) > 3.8) ORDER BY e.editorial, l.titulo
```

#### 23. RIGHT JOIN: todas las migraciones `basico`
> Une las tablas leones_marinos y migraciones usando RIGHT JOIN para asegurar que aparezcan TODAS las migraciones, incluso si el leon marino ya no esta en la tabla leones_marinos.

```sql
SELECT lm.nombre, lm.especie, m.distancia, m.dias FROM leones_marinos lm RIGHT JOIN migraciones m ON lm.id = m.id
```

#### 24. Libros con sus traductores `basico`
> Muestra cada libro con el nombre de su traductor. Une las tablas libros, traduccion y traductores. Ordena por titulo.

```sql
SELECT l.titulo, t.nombre AS traductor FROM libros l JOIN traduccion tr ON l.id = tr.libro_id JOIN traductores t ON t.id = tr.traductor_id ORDER BY l.titulo
```

#### 25. FULL JOIN: verlo todo `intermedio`
> Usa FULL JOIN entre leones_marinos y migraciones para ver todos los registros de ambas tablas. Los valores sin correspondencia apareceran como NULL.

```sql
SELECT lm.nombre, lm.especie, m.distancia, m.dias FROM leones_marinos lm FULL JOIN migraciones m ON lm.id = m.id
```

#### 26. Libros sin puntuaciones `intermedio`
> Encuentra los libros que NO tienen ninguna puntuacion registrada. Usa LEFT JOIN con puntuaciones y filtra por IS NULL.

```sql
SELECT l.titulo FROM libros l LEFT JOIN puntuaciones p ON l.id = p.libro_id WHERE p.libro_id IS NULL ORDER BY l.titulo
```

#### 27. Cuantos libros escribio cada autor `intermedio`
> Muestra cada autor junto con el numero de libros que ha escrito. Usa GROUP BY sobre la tabla autoria. Ordena del mas prolifico al menos.

```sql
SELECT a.nombre, COUNT(au.libro_id) AS libros_escritos FROM autores a JOIN autoria au ON a.id = au.autor_id GROUP BY a.id, a.nombre ORDER BY libros_escritos DESC
```

#### 28. Promedio de puntuacion por editorial `intermedio`
> Calcula la puntuacion promedio de los libros agrupados por editorial. Muestra el nombre de la editorial y el promedio redondeado a 2 decimales. Ordena de mayor a menor promedio. Necesitas unir editoriales, libros y puntuaciones.

```sql
SELECT e.editorial, ROUND(AVG(p.puntuacion)::numeric, 2) AS promedio FROM editoriales e JOIN libros l ON e.id = l.editorial_id JOIN puntuaciones p ON l.id = p.libro_id GROUP BY e.id, e.editorial ORDER BY promedio DESC
```

#### 29. Autores sin libros registrados `avanzado`
> ¿Hay autores en la base de datos que no tienen ningun libro asociado? Usa NOT IN con una subconsulta que obtenga los autor_id de la tabla autoria.

```sql
SELECT nombre FROM autores WHERE id NOT IN (SELECT DISTINCT autor_id FROM autoria) ORDER BY nombre
```

#### 30. Autores con mas de un libro `avanzado`
> Muestra los autores que han escrito mas de un libro. Incluye el nombre y la cantidad. Filtra con HAVING COUNT > 1.

```sql
SELECT a.nombre, COUNT(au.libro_id) AS libros_escritos FROM autores a JOIN autoria au ON a.id = au.autor_id GROUP BY a.id, a.nombre HAVING COUNT(au.libro_id) > 1 ORDER BY libros_escritos DESC
```

#### 31. Distancia total por leon marino `avanzado`
> Para cada leon marino, calcula la distancia total recorrida sumando todas sus migraciones. Muestra el nombre, la especie y la distancia total. Ordena del mas viajero al menos.

```sql
SELECT lm.nombre, lm.especie, SUM(m.distancia) AS distancia_total, SUM(m.dias) AS dias_totales FROM leones_marinos lm JOIN migraciones m ON lm.id = m.id GROUP BY lm.id, lm.nombre, lm.especie ORDER BY distancia_total DESC
```

#### 32. Libro con autor y traductor `avanzado`
> Muestra el titulo de cada libro junto con el nombre de su autor y su traductor. Necesitas unir 5 tablas: libros, autoria, autores, traduccion y traductores. Limita a 15 resultados.

```sql
SELECT l.titulo, a.nombre AS autor, t.nombre AS traductor FROM libros l JOIN autoria au ON l.id = au.libro_id JOIN autores a ON a.id = au.autor_id JOIN traduccion tr ON l.id = tr.libro_id JOIN traductores t ON t.id = tr.traductor_id ORDER BY l.titulo LIMIT 15
```

### Problem Set — DESE
*Asumí el rol de analista de datos del Departamento de Educación de Massachusetts. Resolvé preguntas sobre escuelas, distritos, graduaciones y gastos usando JOIN, GROUP BY y subconsultas.*  
Esquema PostgreSQL: `dese`  
⚠️ Problem Set

#### 1. Mapa de escuelas públicas `basico`
> Tu parro está armando un mapa con todas las escuelas públicas de Massachusetts. Encontrá los nombres y las ciudades de todas las escuelas públicas del estado.
> Ojo: en la tabla `schools` no todo es escuela pública tradicional. Massachusetts también tiene escuelas charter (de administración diferente) y DESE las cuenta aparte. Filtrá solo las de tipo `'Public School'`.

```sql
SELECT name, city FROM schools WHERE type = 'Public School'
```

#### 2. Distritos que ya no operan `basico`
> Tu equipo está archivando datos viejos. Encontrá los nombres de los distritos que ya no están operativos.
> Los distritos que no operan más tienen `"(non-op)"` al final del nombre. Usá LIKE para detectarlos.

```sql
SELECT name FROM districts WHERE name LIKE '%(non-op)%'
```

#### 3. Gasto promedio por estudiante `basico`
> La legislatura de Massachusetts quiere saber cuánto gastaron, en promedio, los distritos por estudiante el año pasado. Encontrá el gasto promedio por estudiante a nivel estatal.
> La columna `per_pupil_expenditure` de `expenditures` trae el gasto promedio por estudiante de cada distrito. Te piden el promedio de esos promedios (todos los distritos pesan igual, sin importar su tamaño). Llamá a la columna `"Average District Per-Pupil Expenditure"`.

```sql
SELECT AVG(per_pupil_expenditure) AS "Average District Per-Pupil Expenditure" FROM expenditures
```

#### 4. Top 10 ciudades con más escuelas públicas `intermedio`
> Hay ciudades con más escuelas públicas que otras. Encontrá las 10 ciudades con más escuelas públicas.
> Mostrá el nombre de la ciudad y cuántas escuelas públicas hay en ella. Ordená de mayor a menor cantidad. Si dos ciudades empatan, ordenalas alfabéticamente.

```sql
SELECT city, COUNT(*) AS n FROM schools WHERE type = 'Public School' GROUP BY city ORDER BY n DESC, city ASC LIMIT 10
```

#### 5. Ciudades con pocas escuelas públicas `intermedio`
> DESE quiere saber en qué ciudades harían falta más escuelas públicas. Encontrá las ciudades que tienen 3 o menos escuelas públicas.
> Mostrá el nombre de la ciudad y cuántas escuelas públicas tiene. Ordená de mayor a menor cantidad. Si empantan, ordená alfabéticamente.

```sql
SELECT city, COUNT(*) AS n FROM schools WHERE type = 'Public School' GROUP BY city HAVING COUNT(*) <= 3 ORDER BY n DESC, city ASC
```

#### 6. Escuelas con 100% de graduación `basico`
> DESE quiere destacar las escuelas que lograron un 100% de graduación. Encontrá los nombres de las escuelas (públicas o charter, da lo mismo) que reportaron un 100% de graduación a tiempo.
> Unite con `graduation_rates` y filtrá por `graduated = 100`.

```sql
SELECT s.name FROM schools s JOIN graduation_rates g ON s.id = g.school_id WHERE g.graduated = 100
```

#### 7. Escuelas del distrito Cambridge `basico`
> DESE está armando un informe sobre las escuelas del distrito de Cambridge. Encontrá los nombres de las escuelas (públicas o charter) del distrito cuyo nombre es `'Cambridge'`.
> Cuidado: la ciudad de Cambridge tiene varios distritos, pero a DESE le interesa solo el distrito que se llama exactamente `'Cambridge'`.

```sql
SELECT s.name FROM schools s JOIN districts d ON s.district_id = d.id WHERE d.name = 'Cambridge'
```

#### 8. Distritos con sus estudiantes `basico`
> Un papá quiere mandar a su hijo a un distrito con muchos estudiantes. Mostrá los nombres de todos los distritos y el número de estudiantes (`pupils`) matriculados en cada uno.
> Uní `districts` con `expenditures` (ahí está `pupils`).

```sql
SELECT d.name, e.pupils FROM districts d JOIN expenditures e ON d.id = e.district_id
```

#### 9. Distrito con menos estudiantes `intermedio`
> Otro papá prefiere un distrito con pocos estudiantes. Encontrá el nombre (o los nombres) del distrito o los distritos con la cantidad mínima de estudiantes.
> Mostrá solo el nombre del distrito. Pista: ordená por `pupils` ascendente y usá LIMIT 1.

```sql
SELECT d.name FROM districts d JOIN expenditures e ON d.id = e.district_id ORDER BY e.pupils ASC LIMIT 1
```

#### 10. Top 10 distritos con mayor gasto por estudiante `intermedio`
> En Massachusetts, el gasto de los distritos depende en parte de los impuestos locales a las propiedades. Encontrá los 10 distritos escolares públicos con mayor gasto por estudiante.
> Mostrá el nombre del distrito y el gasto por estudiante. Filtrá por distritos de tipo `'Public School District'` y ordená de mayor a menor gasto.

```sql
SELECT d.name, e.per_pupil_expenditure FROM districts d JOIN expenditures e ON d.id = e.district_id WHERE d.type = 'Public School District' ORDER BY e.per_pupil_expenditure DESC LIMIT 10
```

#### 11. Gasto vs. graduación `avanzado`
> ¿Habrá relación entre lo que gastan las escuelas y su tasa de graduación? Mostrá los nombres de las escuelas, su gasto por estudiante y su tasa de graduación.
> Ordená las escuelas de mayor a menor gasto por estudiante. Si dos escuelas empatan en gasto, ordenalas por nombre.
> Asumí que cada escuela gasta lo mismo por estudiante que su distrito. Vas a tener que unir `schools` con `graduation_rates` y, a la vez, con `expenditures` (usando el `district_id` de la escuela).

```sql
SELECT s.name, e.per_pupil_expenditure, g.graduated FROM schools s JOIN graduation_rates g ON s.id = g.school_id JOIN expenditures e ON s.district_id = e.district_id ORDER BY e.per_pupil_expenditure DESC, s.name ASC
```

#### 12. Los mejores distritos públicos `avanzado`
> Un papá te pide consejo para encontrar los mejores distritos públicos de Massachusetts. Encontrá los distritos públicos con gasto por estudiante por encima del promedio Y con porcentaje de docentes evaluados como `'exemplary'` por encima del promedio.
> Mostrá el nombre del distrito, su gasto por estudiante y su porcentaje de docentes exemplary. Ordená primero por porcentaje exemplary (de mayor a menor) y luego por gasto por estudiante (de mayor a menor).
> Pista: las subconsultas se pueden poner en muchas partes del SELECT, incluso en el WHERE. Por ejemplo:
> `SELECT col FROM tabla WHERE col > (SELECT AVG(col) FROM tabla)`.

```sql
SELECT d.name, e.per_pupil_expenditure, st.exemplary FROM districts d JOIN expenditures e ON d.id = e.district_id JOIN staff_evaluations st ON d.id = st.district_id WHERE d.type = 'Public School District' AND e.per_pupil_expenditure >     (SELECT AVG(per_pupil_expenditure) FROM expenditures) AND st.exemplary >     (SELECT AVG(exemplary) FROM staff_evaluations) ORDER BY st.exemplary DESC, e.per_pupil_expenditure DESC
```

#### 13. Pregunta libre sobre educación `avanzado`
> Este es un ejercicio libre: inventate una pregunta sobre los datos y respondela con una consulta SQL.
> La regla es que tu consulta use al menos un `JOIN` o una subconsulta. Por ejemplo: ¿qué distrito tiene el mayor porcentaje de docentes calificados como exemplary? ¿Qué ciudad tiene la mayor tasa de deserción (`dropped`)? Lo que se te ocurra, pero que tenga JOIN o subconsulta.
> Como pista, una buena respuesta podría ser: el nombre del distrito con mayor porcentaje de docentes exemplary.
> Solución de ejemplo (podés usar otra):
> `SELECT d.name, st.exemplary FROM districts d JOIN staff_evaluations st ON d.id = st.district_id ORDER BY st.exemplary DESC LIMIT 1`.

```sql
SELECT d.name, st.exemplary FROM districts d JOIN staff_evaluations st ON d.id = st.district_id ORDER BY st.exemplary DESC LIMIT 1
```

### Problem Set — Moneyball
*Sos el analista de los Oakland Athletics en 2001. Con poco presupuesto, encontrá el valor escondido en jugadores que otros equipos no ven. JOIN, agregaciones y subconsultas anidadas.*  
Esquema PostgreSQL: `moneyball`  
⚠️ Problem Set

#### 1. Salario promedio por año `basico`
> Empezá viendo cómo cambió el salario promedio de los jugadores con el tiempo. Encontrá el salario promedio por año.
> - Ordená por año descendente.
> - Redondeá a dos decimales y llamá a la columna `"average salary"`.
> - Tu consulta debe devolver dos columnas: año y salario promedio.

```sql
SELECT year, ROUND(AVG(salary), 2) AS "average salary" FROM salaries GROUP BY year ORDER BY year DESC
```

#### 2. Historial salarial de Cal Ripken Jr. `basico`
> El gerente general te pregunta si conviene cambiar un jugador por Cal Ripken Jr., una estrella que está al final de su carrera. Encontrá el historial de salarios de Cal Ripken Jr.
> Ojo con el nombre: en la base de datos aparece como `first_name = 'Cal'` y `last_name = 'Ripken'` (sin el "Jr."). Te toca a vos buscarlo con esos datos.
> - Ordená por año descendente.
> - Devolvé dos columnas: año y salario.

```sql
SELECT year, salary FROM salaries WHERE player_id = (  SELECT id FROM players   WHERE first_name = 'Cal' AND last_name = 'Ripken') ORDER BY year DESC
```

#### 3. Jonrones de Ken Griffey Jr. `basico`
> El equipo necesita un buen bateador de jonrones. Ken Griffey Jr., ganador de muchos premios, podría ser una buena opción. Encontrá el historial de jonrones (`HR`) de Ken Griffey Jr.
> - Ordená por año descendente.
> - En la base hay dos jugadores llamados Ken Griffey. El que nos interesa nació en 1969 (`birth_year = 1969`).
> - En la BD está como `first_name = 'Ken'` y `last_name = 'Griffey'` (sin "Jr.").
> - Devolvé dos columnas: año y jonrones (`HR`).

```sql
SELECT p.year, p.HR FROM performances p JOIN players pl ON p.player_id = pl.id WHERE pl.first_name = 'Ken' AND pl.last_name = 'Griffey'   AND pl.birth_year = 1969 ORDER BY p.year DESC
```

#### 4. Los 50 jugadores peor pagados del 2001 `intermedio`
> Tenés que recomendar jugadores para fichar. Con el presupuesto al fondo, el gerente quiere saber quiénes cobraron los salarios más bajos en 2001. Encontrá los 50 jugadores peor pagados en el 2001.
> - Ordená por salario, de menor a mayor.
> - Si dos jugadores cobran lo mismo, ordenalos alfabéticamente por nombre y luego por apellido.
> - Si también coinciden en nombre y apellido, ordenalos por el ID del jugador.
> - Devolvé tres columnas: nombre, apellido y salario.

```sql
SELECT pl.first_name, pl.last_name, s.salary FROM salaries s JOIN players pl ON s.player_id = pl.id WHERE s.year = 2001 ORDER BY s.salary ASC, pl.first_name ASC, pl.last_name ASC,          pl.id ASC LIMIT 50
```

#### 5. Equipos de Satchel Paige `intermedio`
> Estás al cuadre hoy. Aunque Satchel Paige ya no juega, encontrá todos los equipos en los que jugó.
> Buscá al jugador con `first_name = 'Satchel'` y `last_name = 'Paige'`. Después listá los equipos (sin repetir) para los que jugó. Devolvé una sola columna con el nombre del equipo.

```sql
SELECT DISTINCT t.name FROM teams t JOIN performances p ON t.id = p.team_id JOIN players pl ON p.player_id = pl.id WHERE pl.first_name = 'Satchel' AND pl.last_name = 'Paige'
```

#### 6. Top 5 equipos por hits en 2001 `intermedio`
> ¿Qué equipos van a ser la competencia más dura para los A's este año? Devolvé los 5 mejores equipos, ordenados por la cantidad total de hits de sus jugadores en 2001.
> - Llamá `"total hits"` a la columna con el total de hits.
> - Ordená de mayor a menor total de hits.
> - Devolvé dos columnas: nombre del equipo y total de hits en 2001.

```sql
SELECT t.name, SUM(p.H) AS "total hits" FROM teams t JOIN performances p ON t.id = p.team_id WHERE p.year = 2001 GROUP BY t.id, t.name ORDER BY "total hits" DESC LIMIT 5
```

#### 7. El jugador mejor pagado de la historia `intermedio`
> Tenés que recomendar qué jugador (o jugadores) NO fichar. Encontrá el nombre del jugador que cobró el salario más alto de toda la historia de las Grandes Ligas.
> Devolvé dos columnas: nombre y apellido. Pista: ordená `salaries` por `salary` descendente y usá `LIMIT 1` (o una subconsulta que devuelva el `player_id` del salario máximo).

```sql
SELECT pl.first_name, pl.last_name FROM players pl JOIN salaries s ON pl.id = s.player_id ORDER BY s.salary DESC LIMIT 1
```

#### 8. Salario del rey de jonrones 2001 `avanzado`
> ¿Cuánto tendrían que pagar los A's para llevarse al que más jonrones pegó en la temporada que acaba de terminar? Encontrá el salario del 2001 del jugador que más jonrones pegó en 2001.
> Devolvé una sola columna: el salario del jugador. Usá `ORDER BY HR DESC LIMIT 1` sobre `performances` del año 2001 y unilo con `salaries` (cuidando que el año del salario coincida con el de la performance).

```sql
SELECT s.salary FROM salaries s JOIN performances p ON s.player_id = p.player_id   AND s.year = p.year WHERE p.year = 2001 ORDER BY p.HR DESC LIMIT 1
```

#### 9. Los 5 equipos que menos pagan (2001) `intermedio`
> ¿Qué salarios pagan los otros equipos? Encontrá los 5 equipos que pagan menos (en promedio salarial) en 2001.
> - Redondeá el promedio a dos decimales y llamá a la columna `"average salary"`.
> - Ordená los equipos por salario promedio, de menor a mayor.
> - Devolvé dos columnas: nombre del equipo y salario promedio.

```sql
SELECT t.name, ROUND(AVG(s.salary), 2) AS "average salary" FROM teams t JOIN salaries s ON t.id = s.team_id WHERE s.year = 2001 GROUP BY t.id, t.name ORDER BY "average salary" ASC LIMIT 5
```

#### 10. Reporte completo: salario + jonrones por año `avanzado`
> El gerente te pidió un reporte con el nombre de cada jugador, su salario por año y la cantidad de jonrones por año. La tabla debe traer: nombre, apellido, salario, jonrones y el año en que cobró ese salario Y pegó esos jonrones.
> Reglas de orden:
> - Primero por ID del jugador (de menor a mayor).
> - Para un mismo jugador, por año descendente.
> - Caso especial: si un jugador tiene varios salarios o performances en el mismo año, ordená primero por jonrones (descendente) y luego por salario (descendente).
> - Asegurate de que, en cada fila, el año del salario y el año de la performance sean el mismo (JOIN por `year`).

```sql
SELECT pl.first_name, pl.last_name, s.salary, p.HR, s.year FROM players pl JOIN salaries s ON pl.id = s.player_id JOIN performances p ON pl.id = p.player_id WHERE s.year = p.year ORDER BY pl.id ASC, s.year DESC, p.HR DESC, s.salary DESC
```

#### 11. Los 10 jugadores más baratos por hit (2001) `avanzado`
> Necesitás jugadores que consigan hits. ¿Quiénes son los más subestimados? Encontrá los 10 jugadores más baratos por hit en 2001.
> - Devolvé tres columnas: nombre, apellido y una llamada `"dollars per hit"`.
> - Calculá `"dollars per hit"` dividiendo el salario de 2001 entre los hits de 2001.
> - Dividir entre 0 hits da `NULL`. Evitalo filtrando los jugadores con 0 hits.
> - Ordená de menor a mayor `"dollars per hit"`. Si empantan, ordená por nombre y luego por apellido, alfabéticamente.
> - Asegurate de que el año del salario y el año de la performance coincidan.
> - Asumí que cada jugador tiene un solo salario y una sola performance en 2001.

```sql
SELECT pl.first_name, pl.last_name,        (s.salary * 1.0 / p.H) AS "dollars per hit" FROM players pl JOIN salaries s ON pl.id = s.player_id JOIN performances p ON pl.id = p.player_id WHERE s.year = 2001 AND p.year = 2001 AND p.H > 0 ORDER BY "dollars per hit" ASC, pl.first_name ASC,          pl.last_name ASC LIMIT 10
```

#### 12. Baratos por hit Y por RBI (2001) `avanzado`
> Los hits están buenos, pero también las carreras impulsadas (RBI). Encontrá los jugadores que estén entre los 10 más baratos por hit Y a la vez entre los 10 más baratos por RBI en 2001.
> - Devolvé dos columnas: nombre y apellido.
> - `salary per RBI` = salario de 2001 / RBI de 2001.
> - Asumí que cada jugador tiene un solo salario y una sola performance en 2001.
> - Ordená por ID de jugador (de menor a mayor).
> - Acordate de lo que aprendiste en los ejercicios 10 y 11 sobre el cruce de salario y performance por el mismo año.
> - Pista: usá dos CTEs (`WITH`) con `LIMIT 10` cada una y unilas con `JOIN` por el ID del jugador.

```sql
WITH per_hit AS (  SELECT pl.id, pl.first_name, pl.last_name,          (s.salary * 1.0 / p.H) AS dph   FROM players pl   JOIN salaries s ON pl.id = s.player_id   JOIN performances p ON pl.id = p.player_id   WHERE s.year = 2001 AND p.year = 2001 AND p.H > 0   ORDER BY dph ASC, pl.first_name ASC, pl.last_name ASC   LIMIT 10), per_rbi AS (  SELECT pl.id, pl.first_name, pl.last_name,          (s.salary * 1.0 / p.RBI) AS dpr   FROM players pl   JOIN salaries s ON pl.id = s.player_id   JOIN performances p ON pl.id = p.player_id   WHERE s.year = 2001 AND p.year = 2001 AND p.RBI > 0   ORDER BY dpr ASC, pl.first_name ASC, pl.last_name ASC   LIMIT 10) SELECT ph.first_name, ph.last_name FROM per_hit ph JOIN per_rbi pr ON ph.id = pr.id ORDER BY ph.id
```

### Problem Set — Packages, Please
*Sos el cartero de Boston. Tres paquetes se perdieron. Con subconsultas y JOIN encontrá dónde están, qué tienen adentro y quién los tiene. Tres misterios que resolver.*  
Esquema PostgreSQL: `packages`  
⚠️ Problem Set

#### 1. Misterio 1 — La carta perdida `avanzado`
> Tu primer reporte de paquete perdido viene de Anneke. Te cuenta:
> > —Señor cartero, me llamo Anneke. Vivo en 900 Somerville Avenue. Hace poquito mandé una cartita especial. Va para mi amiga Varsha, que está empezando una nueva etapa en 2 Finnegan Street. (Esa dirección, le cuento, me dio lidito la primera vez). La carta es una nota de felicitación, un abracito en papel para celebrar el cambio de vida de ella. ¿Puede mirar si ya llegó?
> Encontrá dónde terminó la carta de Anneke. Mostrá la dirección y el tipo de dirección donde quedó.
> Pista: el paquete es el que tiene `contents = 'Congratulatory letter'` y `from_address_id` igual a la dirección de Anneke (900 Somerville Avenue). El último `scan` con `action = 'Drop'` te dice dónde quedó.
> Devolvé dos columnas: `address` y `type`.

```sql
SELECT a.address, a.type FROM scans s JOIN addresses a ON s.address_id = a.id WHERE s.action = 'Drop' AND s.package_id = (  SELECT id FROM packages   WHERE from_address_id = (    SELECT id FROM addresses WHERE address = '900 Somerville Avenue'  ) AND contents = 'Congratulatory letter')
```

#### 2. Misterio 2 — La entrega aviesa `avanzado`
> El segundo reporte viene de un personaje misterioso de fuera. Te cuenta:
> > —Buenas, repartidor de correo. Acordate que hace poquito vine de Fiftyville y le dejé una caja a usté, bien chévere, pa' que la cuidara. Mi socio ya estaba esperando el paquete y no aparece. ¡Si como si le hubiera echado alas y se hubiera volado! ¿Me ayuda a aclarar este misterio? Eso sí, no tiene dirección de remitente. Es el tipo de paquete que le echa más… pato a la hora del baño, si me entiende la vuelta.
> Encontrá dónde quedó el paquete del misterioso. Mostrá la dirección, el tipo y el contenido del paquete.
> Pistas: el paquete no tiene `from_address_id` (es NULL) y su `contents` tiene que ver con un pato (en la base aparece como `'Duck debugger'`). El `action = 'Drop'` final te da la ubicación.
> Devolvé tres columnas: `address`, `type` y `contents`.

```sql
SELECT a.address, a.type, p.contents FROM scans s JOIN addresses a ON s.address_id = a.id JOIN packages p ON s.package_id = p.id WHERE s.action = 'Drop' AND s.package_id = (  SELECT id FROM packages   WHERE from_address_id IS NULL AND contents = 'Duck debugger')
```

#### 3. Misterio 3 — El regalo olvidado `avanzado`
> El tercer reporte viene de un abuelo que vive cerca del correo. Te cuenta:
> > —Ay, disculpe, señor cartero. Resulta que mandé un regalo sorpresivo a mi nieta linda, que vive en 728 Maple Place. Hace como dos semanas. Ya pasaron siete días de la fecha de entrega y me dice ella que sigue esperando, con las manos vacías y el corazón lleno de esperanza. Ya me dio afano, no sé dónde habrá quedado mi paquete. La verdad no me acuerdo qué tiene adentro, pero sí sé que está relleno del cariño que le tengo. ¿Lo podemos rastrear pa' que le alegre el día? Yo lo mandé desde mi casa, en 109 Tileston Street.
> Encontrá dónde está el regalo del abuelo, qué tiene adentro y qué cartero (driver) lo tiene ahora.
> Pistas: el paquete tiene `from_address_id` = 109 Tileston Street y `to_address_id` = 728 Maple Place. El último scan (el de `timestamp` más reciente) te dice dónde está y quién lo tiene.
> Devolvé cuatro columnas: `address`, `type`, `driver_name` (renombrá `name` de `drivers`) y `contents`.

```sql
SELECT a.address, a.type, d.name AS driver_name, p.contents FROM scans s JOIN addresses a ON s.address_id = a.id JOIN drivers d ON s.driver_id = d.id JOIN packages p ON s.package_id = p.id WHERE s.package_id = (  SELECT id FROM packages   WHERE from_address_id = (    SELECT id FROM addresses WHERE address = '109 Tileston Street'  ) AND to_address_id = (    SELECT id FROM addresses WHERE address = '728 Maple Place'  )) ORDER BY s.timestamp DESC LIMIT 1
```

---

*Curso completo: [CS50's Introduction to Databases with SQL](https://cs50.harvard.edu/sql/) — Harvard University. Esta adaptación es open source (MIT).*
