"""Cheatsheet de referencia SQL para la app (sin soluciones de ejercicios)."""

from __future__ import annotations


# Cada categoría tiene una lista de entradas con concepto, sintaxis, ejemplo y nota.
CHEATSHEET: dict[str, list[dict[str, str]]] = {
    "Consultas básicas": [
        {"concepto": "SELECT", "sintaxis": "SELECT col1, col2 FROM tabla", "ejemplo": "SELECT titulo, autor FROM libros", "nota": "Elige columnas. SELECT * trae todas."},
        {"concepto": "LIMIT", "sintaxis": "SELECT ... LIMIT n", "ejemplo": "SELECT * FROM libros LIMIT 10", "nota": "Máximo n filas. Útil para explorar."},
        {"concepto": "DISTINCT", "sintaxis": "SELECT DISTINCT col FROM tabla", "ejemplo": "SELECT DISTINCT editorial_id FROM libros", "nota": "Elimina duplicados."},
        {"concepto": "ORDER BY", "sintaxis": "ORDER BY col [ASC|DESC]", "ejemplo": "SELECT * FROM libros ORDER BY titulo ASC", "nota": "Ordena. ASC ascendente (default), DESC descendente. Varios cols separados por coma."},
        {"concepto": "AS (alias)", "sintaxis": "SELECT col AS alias", "ejemplo": 'SELECT AVG(puntuacion) AS "promedio"', "nota": "Renombra columnas. Con espacios usa comillas dobles."},
    ],
    "Filtrado (WHERE)": [
        {"concepto": "WHERE", "sintaxis": "WHERE condicion", "ejemplo": "SELECT * FROM libros WHERE ano > 2010", "nota": "Filtra filas que cumplen la condición."},
        {"concepto": "Operadores", "sintaxis": "=, !=, <>, <, >, <=, >=", "ejemplo": "WHERE puntuacion >= 4", "nota": "!= y <> son equivalentes (distinto)."},
        {"concepto": "AND / OR / NOT", "sintaxis": "WHERE c1 AND (c2 OR c3)", "ejemplo": "WHERE ano > 2000 AND editorial_id = 3", "nota": "Combina condiciones. Usa paréntesis para agrupar."},
        {"concepto": "IS NULL", "sintaxis": "WHERE col IS NULL", "ejemplo": "SELECT * FROM libros WHERE autor IS NULL", "nota": "Detecta valores ausentes. IS NOT NULL para lo contrario."},
        {"concepto": "IN", "sintaxis": "WHERE col IN (v1, v2, ...)", "ejemplo": "WHERE editorial_id IN (1, 2, 3)", "nota": "Equivalente a varios OR. Acepta subconsultas."},
        {"concepto": "BETWEEN", "sintaxis": "WHERE col BETWEEN a AND b", "ejemplo": "WHERE ano BETWEEN 2000 AND 2010", "nota": "Incluye los extremos. Equivalente a >= a AND <= b."},
        {"concepto": "LIKE / ILIKE", "sintaxis": "WHERE col LIKE 'patrón'", "ejemplo": "WHERE titulo LIKE 'El%'", "nota": "% = cualquier secuencia, _ = un carácter. ILIKE no distingue mayúsculas."},
    ],
    "Funciones de agregación": [
        {"concepto": "COUNT", "sintaxis": "COUNT(*) o COUNT(col)", "ejemplo": "SELECT COUNT(*) FROM libros", "nota": "Cuenta filas. COUNT(col) ignora NULLs."},
        {"concepto": "AVG / SUM", "sintaxis": "AVG(col) / SUM(col)", "ejemplo": "SELECT AVG(puntuacion) FROM puntuaciones", "nota": "Promedio y suma. Ignoran NULLs."},
        {"concepto": "MIN / MAX", "sintaxis": "MIN(col) / MAX(col)", "ejemplo": "SELECT MIN(ano), MAX(ano) FROM libros", "nota": "Mínimo y máximo."},
        {"concepto": "ROUND", "sintaxis": "ROUND(numero, decimales)", "ejemplo": "ROUND(AVG(puntuacion)::numeric, 2)", "nota": "Redondea a n decimales. En PostgreSQL castea con ::numeric si hace falta."},
        {"concepto": "GROUP BY", "sintaxis": "SELECT col, AGG(col2) ... GROUP BY col", "ejemplo": "SELECT editorial_id, COUNT(*) FROM libros GROUP BY editorial_id", "nota": "Agrupa filas por col y aplica agregación a cada grupo."},
        {"concepto": "HAVING", "sintaxis": "GROUP BY col HAVING AGG(col2) > n", "ejemplo": "GROUP BY libro_id HAVING COUNT(*) > 100", "nota": "Como WHERE pero para agregaciones. Va después de GROUP BY."},
    ],
    "JOIN (relacionar tablas)": [
        {"concepto": "INNER JOIN", "sintaxis": "SELECT ... FROM a JOIN b ON a.id = b.a_id", "ejemplo": "SELECT l.titulo, e.editorial FROM libros l JOIN editoriales e ON l.editorial_id = e.id", "nota": "Solo filas que coinciden en ambas tablas."},
        {"concepto": "LEFT JOIN", "sintaxis": "FROM a LEFT JOIN b ON a.id = b.a_id", "ejemplo": "SELECT lm.nombre, m.distancia FROM leones_marinos lm LEFT JOIN migraciones m ON lm.id = m.id", "nota": "Todas las filas de la izquierda. Si no hay coincidencia, NULLs a la derecha."},
        {"concepto": "RIGHT JOIN", "sintaxis": "FROM a RIGHT JOIN b ON a.id = b.a_id", "ejemplo": "SELECT lm.nombre, m.distancia FROM leones_marinos lm RIGHT JOIN migraciones m ON lm.id = m.id", "nota": "Todas las filas de la derecha."},
        {"concepto": "FULL JOIN", "sintaxis": "FROM a FULL JOIN b ON a.id = b.a_id", "ejemplo": "SELECT lm.nombre, m.distancia FROM leones_marinos lm FULL JOIN migraciones m ON lm.id = m.id", "nota": "Todas las filas de ambas tablas (UNION de LEFT y RIGHT)."},
        {"concepto": "NATURAL JOIN", "sintaxis": "FROM a NATURAL JOIN b", "ejemplo": "SELECT * FROM leones_marinos NATURAL JOIN migraciones", "nota": "JOIN automático por columnas con el mismo nombre. Ojo: puede sorprender."},
        {"concepto": "Múltiples JOIN", "sintaxis": "FROM a JOIN b ON ... JOIN c ON ...", "ejemplo": "FROM libros l JOIN autoria au ON l.id=au.libro_id JOIN autores a ON a.id=au.autor_id", "nota": "Encadena JOINs. Cada uno con su ON."},
    ],
    "Subconsultas": [
        {"concepto": "Subconsulta escalar", "sintaxis": "WHERE col = (SELECT ... )", "ejemplo": "SELECT titulo FROM libros WHERE editorial_id = (SELECT id FROM editoriales WHERE editorial = 'Fitzcarraldo Editions')", "nota": "Devuelve un solo valor. Va entre paréntesis."},
        {"concepto": "IN con subconsulta", "sintaxis": "WHERE col IN (SELECT ...)", "ejemplo": "SELECT titulo FROM libros WHERE id IN (SELECT libro_id FROM autoria WHERE autor_id = 5)", "nota": "Subconsulta que devuelve una columna."},
        {"concepto": "Subconsulta en HAVING", "sintaxis": "HAVING AGG(col) > (SELECT AVG(col) FROM ...)", "ejemplo": "HAVING AVG(puntuacion) > (SELECT AVG(puntuacion) FROM puntuaciones)", "nota": "Compara contra un promedio global u otro agregado."},
        {"concepto": "CTE (WITH)", "sintaxis": "WITH nombre AS (SELECT ...) SELECT ... FROM nombre", "ejemplo": "WITH top10 AS (SELECT ... LIMIT 10) SELECT * FROM top10", "nota": "Subconsulta con nombre. Útil para reusar o para legibilidad."},
    ],
    "Conjuntos (UNION / INTERSECT / EXCEPT)": [
        {"concepto": "UNION", "sintaxis": "SELECT ... UNION SELECT ...", "ejemplo": "SELECT nombre FROM autores UNION SELECT nombre FROM traductores", "nota": "Combina resultados, elimina duplicados. UNION ALL los conserva."},
        {"concepto": "INTERSECT", "sintaxis": "SELECT ... INTERSECT SELECT ...", "ejemplo": "SELECT nombre FROM autores INTERSECT SELECT nombre FROM traductores", "nota": "Filas que están en AMBOS resultados."},
        {"concepto": "EXCEPT", "sintaxis": "SELECT ... EXCEPT SELECT ...", "ejemplo": "SELECT nombre FROM traductores EXCEPT SELECT nombre FROM autores", "nota": "Filas del primero que NO están en el segundo."},
    ],
}