from services.ejercicios import Ejercicio


def ejercicios_packages() -> list[Ejercicio]:
    """3 misterios del pset Packages, Please (Boston mail clerk) en español paisa.

    Esquema PostgreSQL: `packages`. Tablas:
      - addresses (id, address, type)
      - packages (id, contents, from_address_id, to_address_id)
      - drivers (id, name)
      - scans (id, driver_id, package_id, address_id, action, timestamp)

    La estructura del pset original son 3 misterios en los que el estudiante
    escribe consultas libremente en `log.sql` y llena `answers.txt`. Aquí los
    convertimos en ejercicios validables: cada misterio pide UNA consulta que
    responda a la pregunta clave del caso.
    """
    return [
        Ejercicio(
            id="pk_01",
            numero=1,
            titulo="Misterio 1 — La carta perdida",
            enunciado=(
                "Tu primer reporte de paquete perdido viene de Anneke. Te cuenta:\n\n"
                "> —Señor cartero, me llamo Anneke. Vivo en 900 Somerville Avenue. "
                "Hace poquito mandé una cartita especial. Va para mi amiga Varsha, "
                "que está empezando una nueva etapa en 2 Finnegan Street. "
                "(Esa dirección, le cuento, me dio lidito la primera vez). "
                "La carta es una nota de felicitación, un abracito en papel para "
                "celebrar el cambio de vida de ella. ¿Puede mirar si ya llegó?\n\n"
                "Encontrá dónde terminó la carta de Anneke. Mostrá la dirección y "
                "el tipo de dirección donde quedó.\n\n"
                "Pista: el paquete es el que tiene `contents = 'Congratulatory "
                "letter'` y `from_address_id` igual a la dirección de Anneke "
                "(900 Somerville Avenue). El último `scan` con `action = 'Drop'` "
                "te dice dónde quedó.\n\n"
                "Devolvé dos columnas: `address` y `type`."
            ),
            dificultad="avanzado",
            sql=(
                "SELECT a.address, a.type FROM scans s "
                "JOIN addresses a ON s.address_id = a.id "
                "WHERE s.action = 'Drop' AND s.package_id = ("
                "  SELECT id FROM packages "
                "  WHERE from_address_id = ("
                "    SELECT id FROM addresses WHERE address = '900 Somerville Avenue'"
                "  ) AND contents = 'Congratulatory letter'"
                ")"
            ),
            esquema="packages",
        ),
        Ejercicio(
            id="pk_02",
            numero=2,
            titulo="Misterio 2 — La entrega aviesa",
            enunciado=(
                "El segundo reporte viene de un personaje misterioso de fuera. "
                "Te cuenta:\n\n"
                "> —Buenas, repartidor de correo. Acordate que hace poquito "
                "vine de Fiftyville y le dejé una caja a usté, bien chévere, "
                "pa' que la cuidara. Mi socio ya estaba esperando el paquete y "
                "no aparece. ¡Si como si le hubiera echado alas y se hubiera "
                "volado! ¿Me ayuda a aclarar este misterio? Eso sí, no tiene "
                "dirección de remitente. Es el tipo de paquete que le echa "
                "más… pato a la hora del baño, si me entiende la vuelta.\n\n"
                "Encontrá dónde quedó el paquete del misterioso. Mostrá la "
                "dirección, el tipo y el contenido del paquete.\n\n"
                "Pistas: el paquete no tiene `from_address_id` (es NULL) y su "
                "`contents` tiene que ver con un pato (en la base aparece "
                "como `'Duck debugger'`). El `action = 'Drop'` final te da la "
                "ubicación.\n\n"
                "Devolvé tres columnas: `address`, `type` y `contents`."
            ),
            dificultad="avanzado",
            sql=(
                "SELECT a.address, a.type, p.contents FROM scans s "
                "JOIN addresses a ON s.address_id = a.id "
                "JOIN packages p ON s.package_id = p.id "
                "WHERE s.action = 'Drop' AND s.package_id = ("
                "  SELECT id FROM packages "
                "  WHERE from_address_id IS NULL AND contents = 'Duck debugger'"
                ")"
            ),
            esquema="packages",
        ),
        Ejercicio(
            id="pk_03",
            numero=3,
            titulo="Misterio 3 — El regalo olvidado",
            enunciado=(
                "El tercer reporte viene de un abuelo que vive cerca del correo. "
                "Te cuenta:\n\n"
                "> —Ay, disculpe, señor cartero. Resulta que mandé un regalo "
                "sorpresivo a mi nieta linda, que vive en 728 Maple Place. "
                "Hace como dos semanas. Ya pasaron siete días de la fecha de "
                "entrega y me dice ella que sigue esperando, con las manos "
                "vacías y el corazón lleno de esperanza. Ya me dio afano, "
                "no sé dónde habrá quedado mi paquete. La verdad no me acuerdo "
                "qué tiene adentro, pero sí sé que está relleno del cariño que "
                "le tengo. ¿Lo podemos rastrear pa' que le alegre el día? "
                "Yo lo mandé desde mi casa, en 109 Tileston Street.\n\n"
                "Encontrá dónde está el regalo del abuelo, qué tiene adentro y "
                "qué cartero (driver) lo tiene ahora.\n\n"
                "Pistas: el paquete tiene `from_address_id` = 109 Tileston "
                "Street y `to_address_id` = 728 Maple Place. El último scan "
                "(el de `timestamp` más reciente) te dice dónde está y quién "
                "lo tiene.\n\n"
                "Devolvé cuatro columnas: `address`, `type`, `driver_name` "
                "(renombrá `name` de `drivers`) y `contents`."
            ),
            dificultad="avanzado",
            sql=(
                "SELECT a.address, a.type, d.name AS driver_name, p.contents "
                "FROM scans s "
                "JOIN addresses a ON s.address_id = a.id "
                "JOIN drivers d ON s.driver_id = d.id "
                "JOIN packages p ON s.package_id = p.id "
                "WHERE s.package_id = ("
                "  SELECT id FROM packages "
                "  WHERE from_address_id = ("
                "    SELECT id FROM addresses WHERE address = '109 Tileston Street'"
                "  ) AND to_address_id = ("
                "    SELECT id FROM addresses WHERE address = '728 Maple Place'"
                "  )"
                ") "
                "ORDER BY s.timestamp DESC LIMIT 1"
            ),
            esquema="packages",
            orden_importa=True,
        ),
    ]