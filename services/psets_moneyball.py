from services.ejercicios import Ejercicio


def ejercicios_moneyball() -> list[Ejercicio]:
    """12 ejercicios del pset Moneyball (béisbol MLB) en español paisa.

    Esquema PostgreSQL: `moneyball`. Tablas:
      - players (id, first_name, last_name, bats, throws, weight, height,
                 debut, final_game, birth_year, birth_month, birth_day,
                 birth_city, birth_state, birth_country)
      - teams (id, year, name, park)
      - salaries (id, player_id, team_id, year, salary)
      - performances (id, player_id, team_id, year, G, AB, H, 2B, 3B, HR, RBI, SB)

    Notas de traducción de términos de béisbol:
      - hit → "hit" (innitentemente hit, queda igual)
      - home run → jonrón
      - at bat → turnos al bate
      - RBI → carreras impulsadas
      - stolen base → base robada
      - double / triple → doble / triple
    """
    return [
        Ejercicio(
            id="mb_01",
            numero=1,
            titulo="Salario promedio por año",
            enunciado=(
                "Empezá viendo cómo cambió el salario promedio de los jugadores "
                "con el tiempo. Encontrá el salario promedio por año.\n\n"
                "- Ordená por año descendente.\n"
                "- Redondeá a dos decimales y llamá a la columna "
                "`\"average salary\"`.\n"
                "- Tu consulta debe devolver dos columnas: año y salario "
                "promedio."
            ),
            dificultad="basico",
            sql=(
                "SELECT year, ROUND(AVG(salary), 2) AS \"average salary\" "
                "FROM salaries GROUP BY year ORDER BY year DESC"
            ),
            esquema="moneyball",
            orden_importa=True,
        ),
        Ejercicio(
            id="mb_02",
            numero=2,
            titulo="Historial salarial de Cal Ripken Jr.",
            enunciado=(
                "El gerente general te pregunta si conviene cambiar un jugador "
                "por Cal Ripken Jr., una estrella que está al final de su "
                "carrera. Encontrá el historial de salarios de Cal Ripken Jr.\n\n"
                "Ojo con el nombre: en la base de datos aparece como "
                "`first_name = 'Cal'` y `last_name = 'Ripken'` (sin el \"Jr.\"). "
                "Te toca a vos buscarlo con esos datos.\n\n"
                "- Ordená por año descendente.\n"
                "- Devolvé dos columnas: año y salario."
            ),
            dificultad="basico",
            sql=(
                "SELECT year, salary FROM salaries "
                "WHERE player_id = ("
                "  SELECT id FROM players "
                "  WHERE first_name = 'Cal' AND last_name = 'Ripken'"
                ") ORDER BY year DESC"
            ),
            esquema="moneyball",
            orden_importa=True,
        ),
        Ejercicio(
            id="mb_03",
            numero=3,
            titulo="Jonrones de Ken Griffey Jr.",
            enunciado=(
                "El equipo necesita un buen bateador de jonrones. Ken Griffey Jr., "
                "ganador de muchos premios, podría ser una buena opción. "
                "Encontrá el historial de jonrones (`HR`) de Ken Griffey Jr.\n\n"
                "- Ordená por año descendente.\n"
                "- En la base hay dos jugadores llamados Ken Griffey. "
                "El que nos interesa nació en 1969 (`birth_year = 1969`).\n"
                "- En la BD está como `first_name = 'Ken'` y "
                "`last_name = 'Griffey'` (sin \"Jr.\").\n"
                "- Devolvé dos columnas: año y jonrones (`HR`)."
            ),
            dificultad="basico",
            sql=(
                "SELECT p.year, p.HR FROM performances p "
                "JOIN players pl ON p.player_id = pl.id "
                "WHERE pl.first_name = 'Ken' AND pl.last_name = 'Griffey' "
                "  AND pl.birth_year = 1969 "
                "ORDER BY p.year DESC"
            ),
            esquema="moneyball",
            orden_importa=True,
        ),
        Ejercicio(
            id="mb_04",
            numero=4,
            titulo="Los 50 jugadores peor pagados del 2001",
            enunciado=(
                "Tenés que recomendar jugadores para fichar. Con el presupuesto "
                "al fondo, el gerente quiere saber quiénes cobraron los salarios "
                "más bajos en 2001. Encontrá los 50 jugadores peor pagados en "
                "el 2001.\n\n"
                "- Ordená por salario, de menor a mayor.\n"
                "- Si dos jugadores cobran lo mismo, ordenalos alfabéticamente "
                "por nombre y luego por apellido.\n"
                "- Si también coinciden en nombre y apellido, ordenalos por "
                "el ID del jugador.\n"
                "- Devolvé tres columnas: nombre, apellido y salario."
            ),
            dificultad="intermedio",
            sql=(
                "SELECT pl.first_name, pl.last_name, s.salary "
                "FROM salaries s JOIN players pl ON s.player_id = pl.id "
                "WHERE s.year = 2001 "
                "ORDER BY s.salary ASC, pl.first_name ASC, pl.last_name ASC, "
                "         pl.id ASC "
                "LIMIT 50"
            ),
            esquema="moneyball",
            orden_importa=True,
        ),
        Ejercicio(
            id="mb_05",
            numero=5,
            titulo="Equipos de Satchel Paige",
            enunciado=(
                "Estás al cuadre hoy. Aunque Satchel Paige ya no juega, "
                "encontrá todos los equipos en los que jugó.\n\n"
                "Buscá al jugador con `first_name = 'Satchel'` y "
                "`last_name = 'Paige'`. Después listá los equipos (sin "
                "repetir) para los que jugó. Devolvé una sola columna con el "
                "nombre del equipo."
            ),
            dificultad="intermedio",
            sql=(
                "SELECT DISTINCT t.name FROM teams t "
                "JOIN performances p ON t.id = p.team_id "
                "JOIN players pl ON p.player_id = pl.id "
                "WHERE pl.first_name = 'Satchel' AND pl.last_name = 'Paige'"
            ),
            esquema="moneyball",
            orden_importa=True,
        ),
        Ejercicio(
            id="mb_06",
            numero=6,
            titulo="Top 5 equipos por hits en 2001",
            enunciado=(
                "¿Qué equipos van a ser la competencia más dura para los A's este "
                "año? Devolvé los 5 mejores equipos, ordenados por la cantidad "
                "total de hits de sus jugadores en 2001.\n\n"
                "- Llamá `\"total hits\"` a la columna con el total de hits.\n"
                "- Ordená de mayor a menor total de hits.\n"
                "- Devolvé dos columnas: nombre del equipo y total de hits en "
                "2001."
            ),
            dificultad="intermedio",
            sql=(
                "SELECT t.name, SUM(p.H) AS \"total hits\" "
                "FROM teams t JOIN performances p ON t.id = p.team_id "
                "WHERE p.year = 2001 "
                "GROUP BY t.id, t.name "
                "ORDER BY \"total hits\" DESC LIMIT 5"
            ),
            esquema="moneyball",
            orden_importa=True,
        ),
        Ejercicio(
            id="mb_07",
            numero=7,
            titulo="El jugador mejor pagado de la historia",
            enunciado=(
                "Tenés que recomendar qué jugador (o jugadores) NO fichar. "
                "Encontrá el nombre del jugador que cobró el salario más alto "
                "de toda la historia de las Grandes Ligas.\n\n"
                "Devolvé dos columnas: nombre y apellido. Pista: ordená "
                "`salaries` por `salary` descendente y usá `LIMIT 1` (o una "
                "subconsulta que devuelva el `player_id` del salario máximo)."
            ),
            dificultad="intermedio",
            sql=(
                "SELECT pl.first_name, pl.last_name FROM players pl "
                "JOIN salaries s ON pl.id = s.player_id "
                "ORDER BY s.salary DESC LIMIT 1"
            ),
            esquema="moneyball",
            orden_importa=True,
        ),
        Ejercicio(
            id="mb_08",
            numero=8,
            titulo="Salario del rey de jonrones 2001",
            enunciado=(
                "¿Cuánto tendrían que pagar los A's para llevarse al que más "
                "jonrones pegó en la temporada que acaba de terminar? Encontrá "
                "el salario del 2001 del jugador que más jonrones pegó en 2001.\n\n"
                "Devolvé una sola columna: el salario del jugador. Usá "
                "`ORDER BY HR DESC LIMIT 1` sobre `performances` del año 2001 "
                "y unilo con `salaries` (cuidando que el año del salario "
                "coincida con el de la performance)."
            ),
            dificultad="avanzado",
            sql=(
                "SELECT s.salary FROM salaries s "
                "JOIN performances p ON s.player_id = p.player_id "
                "  AND s.year = p.year "
                "WHERE p.year = 2001 "
                "ORDER BY p.HR DESC LIMIT 1"
            ),
            esquema="moneyball",
        ),
        Ejercicio(
            id="mb_09",
            numero=9,
            titulo="Los 5 equipos que menos pagan (2001)",
            enunciado=(
                "¿Qué salarios pagan los otros equipos? Encontrá los 5 equipos "
                "que pagan menos (en promedio salarial) en 2001.\n\n"
                "- Redondeá el promedio a dos decimales y llamá a la columna "
                "`\"average salary\"`.\n"
                "- Ordená los equipos por salario promedio, de menor a mayor.\n"
                "- Devolvé dos columnas: nombre del equipo y salario promedio."
            ),
            dificultad="intermedio",
            sql=(
                "SELECT t.name, ROUND(AVG(s.salary), 2) AS \"average salary\" "
                "FROM teams t JOIN salaries s ON t.id = s.team_id "
                "WHERE s.year = 2001 "
                "GROUP BY t.id, t.name "
                "ORDER BY \"average salary\" ASC LIMIT 5"
            ),
            esquema="moneyball",
            orden_importa=True,
        ),
        Ejercicio(
            id="mb_10",
            numero=10,
            titulo="Reporte completo: salario + jonrones por año",
            enunciado=(
                "El gerente te pidió un reporte con el nombre de cada jugador, "
                "su salario por año y la cantidad de jonrones por año. La tabla "
                "debe traer: nombre, apellido, salario, jonrones y el año en "
                "que cobró ese salario Y pegó esos jonrones.\n\n"
                "Reglas de orden:\n"
                "- Primero por ID del jugador (de menor a mayor).\n"
                "- Para un mismo jugador, por año descendente.\n"
                "- Caso especial: si un jugador tiene varios salarios o "
                "performances en el mismo año, ordená primero por jonrones "
                "(descendente) y luego por salario (descendente).\n"
                "- Asegurate de que, en cada fila, el año del salario y el "
                "año de la performance sean el mismo (JOIN por `year`)."
            ),
            dificultad="avanzado",
            sql=(
                "SELECT pl.first_name, pl.last_name, s.salary, p.HR, s.year "
                "FROM players pl "
                "JOIN salaries s ON pl.id = s.player_id "
                "JOIN performances p ON pl.id = p.player_id "
                "WHERE s.year = p.year "
                "ORDER BY pl.id ASC, s.year DESC, p.HR DESC, s.salary DESC"
            ),
            esquema="moneyball",
            orden_importa=True,
        ),
        Ejercicio(
            id="mb_11",
            numero=11,
            titulo="Los 10 jugadores más baratos por hit (2001)",
            enunciado=(
                "Necesitás jugadores que consigan hits. ¿Quiénes son los más "
                "subestimados? Encontrá los 10 jugadores más baratos por hit "
                "en 2001.\n\n"
                "- Devolvé tres columnas: nombre, apellido y una llamada "
                "`\"dollars per hit\"`.\n"
                "- Calculá `\"dollars per hit\"` dividiendo el salario de 2001 "
                "entre los hits de 2001.\n"
                "- Dividir entre 0 hits da `NULL`. Evitalo filtrando los "
                "jugadores con 0 hits.\n"
                "- Ordená de menor a mayor `\"dollars per hit\"`. Si empantan, "
                "ordená por nombre y luego por apellido, alfabéticamente.\n"
                "- Asegurate de que el año del salario y el año de la "
                "performance coincidan.\n"
                "- Asumí que cada jugador tiene un solo salario y una sola "
                "performance en 2001."
            ),
            dificultad="avanzado",
            sql=(
                "SELECT pl.first_name, pl.last_name, "
                "       (s.salary * 1.0 / p.H) AS \"dollars per hit\" "
                "FROM players pl "
                "JOIN salaries s ON pl.id = s.player_id "
                "JOIN performances p ON pl.id = p.player_id "
                "WHERE s.year = 2001 AND p.year = 2001 AND p.H > 0 "
                "ORDER BY \"dollars per hit\" ASC, pl.first_name ASC, "
                "         pl.last_name ASC "
                "LIMIT 10"
            ),
            esquema="moneyball",
            orden_importa=True,
        ),
        Ejercicio(
            id="mb_12",
            numero=12,
            titulo="Baratos por hit Y por RBI (2001)",
            enunciado=(
                "Los hits están buenos, pero también las carreras impulsadas "
                "(RBI). Encontrá los jugadores que estén entre los 10 más "
                "baratos por hit Y a la vez entre los 10 más baratos por RBI "
                "en 2001.\n\n"
                "- Devolvé dos columnas: nombre y apellido.\n"
                "- `salary per RBI` = salario de 2001 / RBI de 2001.\n"
                "- Asumí que cada jugador tiene un solo salario y una sola "
                "performance en 2001.\n"
                "- Ordená por ID de jugador (de menor a mayor).\n"
                "- Acordate de lo que aprendiste en los ejercicios 10 y 11 "
                "sobre el cruce de salario y performance por el mismo año.\n"
                "- Pista: usá dos CTEs (`WITH`) con `LIMIT 10` cada una y "
                "unilas con `JOIN` por el ID del jugador."
            ),
            dificultad="avanzado",
            sql=(
                "WITH per_hit AS ("
                "  SELECT pl.id, pl.first_name, pl.last_name, "
                "         (s.salary * 1.0 / p.H) AS dph "
                "  FROM players pl "
                "  JOIN salaries s ON pl.id = s.player_id "
                "  JOIN performances p ON pl.id = p.player_id "
                "  WHERE s.year = 2001 AND p.year = 2001 AND p.H > 0 "
                "  ORDER BY dph ASC, pl.first_name ASC, pl.last_name ASC "
                "  LIMIT 10"
                "), per_rbi AS ("
                "  SELECT pl.id, pl.first_name, pl.last_name, "
                "         (s.salary * 1.0 / p.RBI) AS dpr "
                "  FROM players pl "
                "  JOIN salaries s ON pl.id = s.player_id "
                "  JOIN performances p ON pl.id = p.player_id "
                "  WHERE s.year = 2001 AND p.year = 2001 AND p.RBI > 0 "
                "  ORDER BY dpr ASC, pl.first_name ASC, pl.last_name ASC "
                "  LIMIT 10"
                ") "
                "SELECT ph.first_name, ph.last_name "
                "FROM per_hit ph JOIN per_rbi pr ON ph.id = pr.id "
                "ORDER BY ph.id"
            ),
            esquema="moneyball",
            orden_importa=True,
        ),
    ]