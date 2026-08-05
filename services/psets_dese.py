from services.ejercicios import Ejercicio


def ejercicios_dese() -> list[Ejercicio]:
    """13 ejercicios del pset DESE (Massachusetts education) en español paisa.

    Esquema PostgreSQL: `dese`. Tablas:
      - districts (id, name, type, city, state, zip)
      - schools (id, district_id, name, type, city, state, zip)
      - graduation_rates (id, school_id, graduated, dropped, excluded)
      - expenditures (id, district_id, pupils, per_pupil_expenditure)
      - staff_evaluations (id, district_id, evaluated, exemplary, proficient,
                          needs_improvement, unsatisfactory)
    """
    return [
        Ejercicio(
            id="dese_01",
            numero=1,
            titulo="Mapa de escuelas públicas",
            enunciado=(
                "Tu parro está armando un mapa con todas las escuelas públicas de "
                "Massachusetts. Encontrá los nombres y las ciudades de todas las "
                "escuelas públicas del estado.\n\n"
                "Ojo: en la tabla `schools` no todo es escuela pública tradicional. "
                "Massachusetts también tiene escuelas charter (de administración "
                "diferente) y DESE las cuenta aparte. Filtrá solo las de tipo "
                "`'Public School'`."
            ),
            dificultad="basico",
            sql=(
                "SELECT name, city FROM schools "
                "WHERE type = 'Public School'"
            ),
            esquema="dese",
            orden_importa=True,
        ),
        Ejercicio(
            id="dese_02",
            numero=2,
            titulo="Distritos que ya no operan",
            enunciado=(
                "Tu equipo está archivando datos viejos. Encontrá los nombres "
                "de los distritos que ya no están operativos.\n\n"
                "Los distritos que no operan más tienen `\"(non-op)\"` al final "
                "del nombre. Usá LIKE para detectarlos."
            ),
            dificultad="basico",
            sql=(
                "SELECT name FROM districts "
                "WHERE name LIKE '%(non-op)%'"
            ),
            esquema="dese",
            orden_importa=True,
        ),
        Ejercicio(
            id="dese_03",
            numero=3,
            titulo="Gasto promedio por estudiante",
            enunciado=(
                "La legislatura de Massachusetts quiere saber cuánto gastaron, "
                "en promedio, los distritos por estudiante el año pasado. "
                "Encontrá el gasto promedio por estudiante a nivel estatal.\n\n"
                "La columna `per_pupil_expenditure` de `expenditures` trae el "
                "gasto promedio por estudiante de cada distrito. Te piden el "
                "promedio de esos promedios (todos los distritos pesan igual, "
                "sin importar su tamaño). Llamá a la columna "
                "`\"Average District Per-Pupil Expenditure\"`."
            ),
            dificultad="basico",
            sql=(
                "SELECT AVG(per_pupil_expenditure) "
                "AS \"Average District Per-Pupil Expenditure\" "
                "FROM expenditures"
            ),
            esquema="dese",
        ),
        Ejercicio(
            id="dese_04",
            numero=4,
            titulo="Top 10 ciudades con más escuelas públicas",
            enunciado=(
                "Hay ciudades con más escuelas públicas que otras. Encontrá "
                "las 10 ciudades con más escuelas públicas.\n\n"
                "Mostrá el nombre de la ciudad y cuántas escuelas públicas hay "
                "en ella. Ordená de mayor a menor cantidad. Si dos ciudades "
                "empatan, ordenalas alfabéticamente."
            ),
            dificultad="intermedio",
            sql=(
                "SELECT city, COUNT(*) AS n FROM schools "
                "WHERE type = 'Public School' "
                "GROUP BY city "
                "ORDER BY n DESC, city ASC "
                "LIMIT 10"
            ),
            esquema="dese",
            orden_importa=True,
        ),
        Ejercicio(
            id="dese_05",
            numero=5,
            titulo="Ciudades con pocas escuelas públicas",
            enunciado=(
                "DESE quiere saber en qué ciudades harían falta más escuelas "
                "públicas. Encontrá las ciudades que tienen 3 o menos escuelas "
                "públicas.\n\n"
                "Mostrá el nombre de la ciudad y cuántas escuelas públicas tiene. "
                "Ordená de mayor a menor cantidad. Si empantan, ordená "
                "alfabéticamente."
            ),
            dificultad="intermedio",
            sql=(
                "SELECT city, COUNT(*) AS n FROM schools "
                "WHERE type = 'Public School' "
                "GROUP BY city "
                "HAVING COUNT(*) <= 3 "
                "ORDER BY n DESC, city ASC"
            ),
            esquema="dese",
            orden_importa=True,
        ),
        Ejercicio(
            id="dese_06",
            numero=6,
            titulo="Escuelas con 100% de graduación",
            enunciado=(
                "DESE quiere destacar las escuelas que lograron un 100% de "
                "graduación. Encontrá los nombres de las escuelas (públicas o "
                "charter, da lo mismo) que reportaron un 100% de graduación a "
                "tiempo.\n\n"
                "Unite con `graduation_rates` y filtrá por `graduated = 100`."
            ),
            dificultad="basico",
            sql=(
                "SELECT s.name FROM schools s "
                "JOIN graduation_rates g ON s.id = g.school_id "
                "WHERE g.graduated = 100"
            ),
            esquema="dese",
            orden_importa=True,
        ),
        Ejercicio(
            id="dese_07",
            numero=7,
            titulo="Escuelas del distrito Cambridge",
            enunciado=(
                "DESE está armando un informe sobre las escuelas del distrito "
                "de Cambridge. Encontrá los nombres de las escuelas (públicas "
                "o charter) del distrito cuyo nombre es `'Cambridge'`.\n\n"
                "Cuidado: la ciudad de Cambridge tiene varios distritos, pero a "
                "DESE le interesa solo el distrito que se llama exactamente "
                "`'Cambridge'`."
            ),
            dificultad="basico",
            sql=(
                "SELECT s.name FROM schools s "
                "JOIN districts d ON s.district_id = d.id "
                "WHERE d.name = 'Cambridge'"
            ),
            esquema="dese",
            orden_importa=True,
        ),
        Ejercicio(
            id="dese_08",
            numero=8,
            titulo="Distritos con sus estudiantes",
            enunciado=(
                "Un papá quiere mandar a su hijo a un distrito con muchos "
                "estudiantes. Mostrá los nombres de todos los distritos y el "
                "número de estudiantes (`pupils`) matriculados en cada uno.\n\n"
                "Uní `districts` con `expenditures` (ahí está `pupils`)."
            ),
            dificultad="basico",
            sql=(
                "SELECT d.name, e.pupils FROM districts d "
                "JOIN expenditures e ON d.id = e.district_id"
            ),
            esquema="dese",
        ),
        Ejercicio(
            id="dese_09",
            numero=9,
            titulo="Distrito con menos estudiantes",
            enunciado=(
                "Otro papá prefiere un distrito con pocos estudiantes. Encontrá "
                "el nombre (o los nombres) del distrito o los distritos con la "
                "cantidad mínima de estudiantes.\n\n"
                "Mostrá solo el nombre del distrito. Pista: ordená por `pupils` "
                "ascendente y usá LIMIT 1."
            ),
            dificultad="intermedio",
            sql=(
                "SELECT d.name FROM districts d "
                "JOIN expenditures e ON d.id = e.district_id "
                "ORDER BY e.pupils ASC LIMIT 1"
            ),
            esquema="dese",
        ),
        Ejercicio(
            id="dese_10",
            numero=10,
            titulo="Top 10 distritos con mayor gasto por estudiante",
            enunciado=(
                "En Massachusetts, el gasto de los distritos depende en parte "
                "de los impuestos locales a las propiedades. Encontrá los 10 "
                "distritos escolares públicos con mayor gasto por estudiante.\n\n"
                "Mostrá el nombre del distrito y el gasto por estudiante. "
                "Filtrá por distritos de tipo `'Public School District'` y "
                "ordená de mayor a menor gasto."
            ),
            dificultad="intermedio",
            sql=(
                "SELECT d.name, e.per_pupil_expenditure FROM districts d "
                "JOIN expenditures e ON d.id = e.district_id "
                "WHERE d.type = 'Public School District' "
                "ORDER BY e.per_pupil_expenditure DESC "
                "LIMIT 10"
            ),
            esquema="dese",
            orden_importa=True,
        ),
        Ejercicio(
            id="dese_11",
            numero=11,
            titulo="Gasto vs. graduación",
            enunciado=(
                "¿Habrá relación entre lo que gastan las escuelas y su tasa de "
                "graduación? Mostrá los nombres de las escuelas, su gasto por "
                "estudiante y su tasa de graduación.\n\n"
                "Ordená las escuelas de mayor a menor gasto por estudiante. "
                "Si dos escuelas empatan en gasto, ordenalas por nombre.\n\n"
                "Asumí que cada escuela gasta lo mismo por estudiante que su "
                "distrito. Vas a tener que unir `schools` con `graduation_rates` "
                "y, a la vez, con `expenditures` (usando el `district_id` de la "
                "escuela)."
            ),
            dificultad="avanzado",
            sql=(
                "SELECT s.name, e.per_pupil_expenditure, g.graduated "
                "FROM schools s "
                "JOIN graduation_rates g ON s.id = g.school_id "
                "JOIN expenditures e ON s.district_id = e.district_id "
                "ORDER BY e.per_pupil_expenditure DESC, s.name ASC"
            ),
            esquema="dese",
            orden_importa=True,
        ),
        Ejercicio(
            id="dese_12",
            numero=12,
            titulo="Los mejores distritos públicos",
            enunciado=(
                "Un papá te pide consejo para encontrar los mejores distritos "
                "públicos de Massachusetts. Encontrá los distritos públicos con "
                "gasto por estudiante por encima del promedio Y con porcentaje "
                "de docentes evaluados como `'exemplary'` por encima del "
                "promedio.\n\n"
                "Mostrá el nombre del distrito, su gasto por estudiante y su "
                "porcentaje de docentes exemplary. Ordená primero por "
                "porcentaje exemplary (de mayor a menor) y luego por gasto por "
                "estudiante (de mayor a menor).\n\n"
                "Pista: las subconsultas se pueden poner en muchas partes del "
                "SELECT, incluso en el WHERE. Por ejemplo:\n"
                "`SELECT col FROM tabla WHERE col > (SELECT AVG(col) FROM tabla)`."
            ),
            dificultad="avanzado",
            sql=(
                "SELECT d.name, e.per_pupil_expenditure, st.exemplary "
                "FROM districts d "
                "JOIN expenditures e ON d.id = e.district_id "
                "JOIN staff_evaluations st ON d.id = st.district_id "
                "WHERE d.type = 'Public School District' "
                "AND e.per_pupil_expenditure > "
                "    (SELECT AVG(per_pupil_expenditure) FROM expenditures) "
                "AND st.exemplary > "
                "    (SELECT AVG(exemplary) FROM staff_evaluations) "
                "ORDER BY st.exemplary DESC, e.per_pupil_expenditure DESC"
            ),
            esquema="dese",
            orden_importa=True,
        ),
        Ejercicio(
            id="dese_13",
            numero=13,
            titulo="Pregunta libre sobre educación",
            enunciado=(
                "Este es un ejercicio libre: inventate una pregunta sobre los "
                "datos y respondela con una consulta SQL.\n\n"
                "La regla es que tu consulta use al menos un `JOIN` o una "
                "subconsulta. Por ejemplo: ¿qué distrito tiene el mayor "
                "porcentaje de docentes calificados como exemplary? ¿Qué "
                "ciudad tiene la mayor tasa de deserción (`dropped`)? Lo que "
                "se te ocurra, pero que tenga JOIN o subconsulta.\n\n"
                "Como pista, una buena respuesta podría ser: el nombre del "
                "distrito con mayor porcentaje de docentes exemplary.\n"
                "Solución de ejemplo (podés usar otra):\n"
                "`SELECT d.name, st.exemplary FROM districts d "
                "JOIN staff_evaluations st ON d.id = st.district_id "
                "ORDER BY st.exemplary DESC LIMIT 1`."
            ),
            dificultad="avanzado",
            sql=(
                "SELECT d.name, st.exemplary FROM districts d "
                "JOIN staff_evaluations st ON d.id = st.district_id "
                "ORDER BY st.exemplary DESC LIMIT 1"
            ),
            esquema="dese",
        ),
    ]