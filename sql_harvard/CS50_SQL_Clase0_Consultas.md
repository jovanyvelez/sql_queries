# Clase 0

## Tabla de Contenidos

- [Introduccion](#introduccion)
- [Que es una Base de Datos?](#que-es-una-base-de-datos)
- [SQL](#sql)
  - [Preguntas](#preguntas)
- [Primeros Pasos con PostgreSQL](#primeros-pasos-con-postgresql)
- [Consejos para la Terminal](#consejos-para-la-terminal)
- [SELECT](#select)
  - [Preguntas](#preguntas-1)
- [LIMIT](#limit)
- [WHERE](#where)
- [NULL](#null)
- [LIKE](#like)
  - [Preguntas](#preguntas-2)
- [Rangos](#rangos)
  - [Preguntas](#preguntas-3)
- [ORDER BY](#order-by)
  - [Preguntas](#preguntas-4)
- [Funciones de Agregacion](#funciones-de-agregacion)
  - [Preguntas](#preguntas-5)
- [Fin](#fin)

---

## Introduccion

- Las bases de datos (y SQL) son herramientas que pueden usarse para interactuar, almacenar y gestionar informacion. Aunque las herramientas que usamos en este curso son nuevas, una base de datos es una idea antiquisima.
- Mira este diagrama de hace unos miles de anos. Tiene filas y columnas, y parece contener estipendios para trabajadores de un templo. Podriamos llamar a este diagrama una tabla, o incluso una hoja de calculo.

![Tabla con Estipendios de Trabajadores del Templo](images/templeworkerstipends.jpg)

- Basandonos en lo que vemos en el diagrama anterior, podemos concluir que:
  - Una tabla almacena un conjunto de informacion (en este caso, estipendios de trabajadores).
  - Cada fila en una tabla almacena un elemento de ese conjunto (en este caso, un trabajador).
  - Cada columna tiene algun atributo de ese elemento (en este caso, el estipendio para un mes en particular).
- Consideremos ahora un contexto moderno. Digamos que eres un bibliotecario encargado de organizar informacion sobre los titulos de libros y autores en este diagrama.

![Titulos de Libros y Autores - Sin Organizar](images/books.jpg)

- Una forma de organizar la informacion seria tener cada titulo de libro seguido de su autor, como se muestra a continuacion.

![Tabla con Titulos de Libros seguido por Autor](images/bookstable.jpg)

  - Observa que cada libro es ahora una fila en esta tabla.
  - Cada fila tiene dos columnas, cada una un atributo diferente del libro (titulo del libro y autor).
- En la era de la informacion actual, podemos almacenar nuestras tablas usando software como Google Sheets en lugar de papel o tablas de piedra. Sin embargo, en este curso hablaremos de bases de datos y no de hojas de calculo.
- Tres razones para ir mas alla de las hojas de calculo a las bases de datos son:
  - **Escala**: Las bases de datos pueden almacenar no solo elementos que llegan a decenas de miles, sino incluso millones y miles de millones.
  - **Capacidad de Actualizacion**: Las bases de datos pueden manejar multiples actualizaciones de datos en un segundo.
  - **Velocidad**: Las bases de datos permiten una recuperacion mas rapida de informacion. Esto se debe a que las bases de datos nos dan acceso a diferentes algoritmos para recuperar informacion. En contraste, las hojas de calculo que simplemente permiten el uso de Ctrl+F o Cmd+F para atravesar resultados uno por uno.

---

## Que es una Base de Datos?

- Una base de datos es una forma de organizar datos tal que puedes realizar cuatro operaciones sobre ella:
  - crear
  - leer
  - actualizar
  - eliminar
- Un sistema de gestion de bases de datos (DBMS) es una forma de interactuar con una base de datos usando una interfaz grafica o un lenguaje textual.
- Ejemplos de DBMS: MySQL, Oracle, PostgreSQL, SQLite, Microsoft Access, MongoDB, etc.
- La eleccion de un DBMS dependeria de factores como:
  - **Costo**: software propietaria vs. gratuito,
  - **Cantidad de soporte**: software gratuito y de codigo abierto como MySQL, PostgreSQL y SQLite vienen con la desventaja de tener que configurar la base de datos uno mismo,
  - **Peso**: sistemas mas completos como MySQL o PostgreSQL son mas pesados y requieren mas computo para ejecutarse que sistemas como SQLite.
- En este curso, comenzaremos con PostgreSQL y luego pasaremos a MySQL.

---

## SQL

- SQL significa Structured Query Language (Lenguaje de Consultas Estructurado). Es un lenguaje usado para interactuar con bases de datos, a traves del cual puedes crear, leer, actualizar y eliminar datos en una base de datos. Algunas notas importantes sobre SQL:
  - es estructurado, como veremos en este curso,
  - tiene algunas palabras clave que pueden usarse para interactuar con la base de datos, y
  - es un lenguaje de consultas, puede usarse para hacer preguntas sobre datos dentro de una base de datos.
- En esta leccion, aprenderemos como escribir algunas consultas SQL simples.

### Preguntas

> ¿Existen subconjuntos de SQL?

- SQL es un estandar tanto del American National Standards Institute (ANSI) como de la International Organization for Standardization (ISO). La mayoria de los DBMS soportan algun subconjunto del lenguaje SQL. Entonces, por ejemplo, para PostgreSQL, estamos usando un subconjunto de SQL que es soportado por PostgreSQL. Si quisieramos移植 nuestro codigo a un sistema diferente como MySQL, es probable que tuvieramos que cambiar parte de la sintaxis.

---

## Primeros Pasos con PostgreSQL

- Vale la pena notar que PostgreSQL es un sistema de base de datos robusto utilizado en muchas aplicaciones incluyendo sitios web, aplicaciones empresariales y sistemas de analisis de datos.
- Ahora, consideremos una base de datos de libros que han estado en la lista larga del International Booker Prize. Cada ano, hay 13 libros en la lista larga y nuestra base de datos contiene 5 anos de estas listas largas.
- Antes de comenzar a interactuar con esta base de datos:
  - Inicia sesion en Visual Studio Code for CS50. Aqui es donde escribiremos codigo y editaremos archivos.
  - El entorno PostgreSQL ya esta configurado en tu sistema. Accede a el mediante la terminal con `psql`.

---

## Consejos para la Terminal

Aqui hay algunos consejos utiles para escribir codigo SQL en la terminal.

- Para limpiar la pantalla de la terminal, presiona Ctrl + L.
- Para obtener la instruccion(es) ejecutada(s) previamente en la terminal, presiona la tecla Flecha hacia Arriba.
- Si tu consulta SQL es demasiado larga y se envuelve en la terminal, puedes presionar enter y continuar escribiendo la consulta en la siguiente linea.
- Para salir de una base de datos o del entorno psql, usa `\q`.

---

## SELECT

- ¿Que datos hay realmente en nuestra base de datos? Para responder esto, usaremos nuestra primera palabra clave SQL, `SELECT`, que nos permite seleccionar algunas (o todas) las filas de una tabla dentro de la base de datos.
- En el entorno psql, ejecuta:

```sql
SELECT *
FROM "lista_larga";
```

Esto selecciona todas las filas de la tabla llamada `lista_larga`.

- La salida que obtenemos contiene todas las columnas de todas las filas en esta tabla, que es muchos datos. Podemos simplificarlo seleccionando una columna en particular, digamos el titulo, de la tabla. Intentemos:

```sql
SELECT "titulo"
FROM "lista_larga";
```

- Ahora, vemos una lista de los titulos en esta tabla. ¿Pero que pasa si queremos ver titulos y autores en nuestros resultados de busqueda? Para esto, ejecutamos:

```sql
SELECT "titulo", "autor"
FROM lista_larga;
```

### Preguntas

> ¿Es necesario usar las comillas dobles (“”) alrededor de los nombres de tablas y columnas?

- Es buena practica usar comillas dobles alrededor de los nombres de tablas y columnas, que se llaman identificadores SQL. SQL tambien tiene cadenas de texto y usamos comillas simples alrededor de las cadenas para diferenciarlas de los identificadores.

> ¿De donde vienen los datos en esta base de datos?

- Esta base de datos contiene datos de varias fuentes.
- Las listas largas de libros ( anos 2018—2023) vienen del sitio web del Booker Prize.
- Las calificaciones y otra informacion sobre estos libros viene de Goodreads.

---

## LIMIT

- Si una base de datos tuviera millones de filas, podria no tener sentido seleccionar todas sus filas. En su lugar, podriamos querer solo echar un vistazo a los datos que contiene. Usamos la palabra clave SQL `LIMIT` para especificar el numero de filas en la salida de la consulta.

```sql
SELECT "titulo"
FROM "lista_larga"
LIMIT 10;
```

Esta consulta nos da los primeros 10 titulos en la base de datos. Los titulos estan ordenados de la misma manera en la salida de esta consulta como estan en la base de datos.

---

## WHERE

- La palabra clave `WHERE` se usa para seleccionar filas basandose en una condicion; devolvera las filas para las cuales la condicion especificada es verdadera.

```sql
SELECT "titulo", "autor"
FROM "lista_larga"
WHERE "anio" = 2023;
```

Esto nos da los titulos y autores de los libros en la lista larga en 2023. Nota que `2023` no esta entre comillas porque es un entero, no una cadena o identificador.

- Los operadores que pueden usarse para especificar condiciones en SQL son `=` ("igual a"), `!=` ("no igual a") y `<>` (tambien "no igual a").
- Para seleccionar los libros que no son ediciones de tapa dura, podemos ejecutar la consulta:

```sql
SELECT "titulo", "formato"
FROM "lista_larga"
WHERE "formato" != 'hardcover';
```

  - Nota que `hardcover` esta entre comillas simples porque es una cadena SQL y no un identificador.

- `!=` puede reemplazarse con el operador `<>` para obtener los mismos resultados. La consulta modificada seria:

```sql
SELECT "titulo", "formato"
FROM "lista_larga"
WHERE "formato" <> 'hardcover';
```

- Otra forma de obtener los mismos resultados es usar la palabra clave SQL `NOT`. La consulta modificada seria:

```sql
SELECT "titulo", "formato"
FROM "lista_larga"
WHERE NOT "formato" = 'hardcover';
```

- Para combinar condiciones, podemos usar las palabras clave SQL `AND` y `OR`. Tambien podemos usar parentesis para indicar como combinar las condiciones en una declaracion condicional compuesta.
- Para seleccionar los titulos y autores de los libros en la lista larga en 2022 o 2023:

```sql
SELECT "titulo", "autor"
FROM "lista_larga"
WHERE "anio" = 2022 OR "anio" = 2023;
```

- Para seleccionar los libros en la lista larga en 2022 o 2023 que **no** fueron de tapa dura:

```sql
SELECT "titulo", "formato"
FROM "lista_larga"
WHERE ("anio" = 2022 OR "anio" = 2023) AND "formato" != 'hardcover';
```

Aqui, los parentesis indican que la clausula `OR` debe evaluarse antes que la clausula `AND`.

---

## NULL

- Es posible que las tablas tengan datos faltantes. `NULL` es un tipo usado para indicar que ciertos datos no tienen un valor, o no existen en la tabla.
- Por ejemplo, los libros en nuestra base de datos tienen un traductor junto con un autor. Sin embargo, solo algunos de los libros han sido traducidos al ingles. Para otros libros, el valor del traductor sera `NULL`.
- Las condiciones usadas con `NULL` son `IS NULL` e `IS NOT NULL`.
- Para seleccionar los libros para los cuales no existen traductores, podemos ejecutar:

```sql
SELECT "titulo", "traductor"
FROM "lista_larga"
WHERE "traductor" IS NULL;
```

- Intentemos lo contrario: seleccionar los libros para los cuales si existen traductores.

```sql
SELECT "titulo", "traductor"
FROM "lista_larga"
WHERE "traductor" IS NOT NULL;
```

---

## LIKE

- Esta palabra clave se usa para seleccionar datos que coinciden aproximadamente con la cadena especificada. Por ejemplo, `LIKE` podria usarse para seleccionar libros que tienen una cierta palabra o frase en su titulo.
- `LIKE` se combina con los operadores `%` (coincide con cualquier caracter alrededor de una cadena dada) y `_` (coincide con un solo caracter).
- Para seleccionar los libros con la palabra "love" en sus titulos, podemos ejecutar:

```sql
SELECT "titulo"
FROM "lista_larga"
WHERE "titulo" LIKE '%love%';
```

`%` coincide con 0 o mas caracteres, entonces esta consulta coincidiria con titulos de libros que tienen 0 o mas caracteres antes y despues de "love", es decir, titulos que contienen "love".

- Para seleccionar los libros cuyo titulo comienza con "The", podemos ejecutar:

```sql
SELECT "titulo"
FROM "lista_larga"
WHERE "titulo" LIKE 'The%';
```

- La consulta anterior tambien podria devolver libros cuyos titulos comienzan con "Their" o "They". Para seleccionar solo los libros cuyos titulos comienzan con la **palabra** "The", podemos agregar un espacio.

```sql
SELECT "titulo"
FROM "lista_larga"
WHERE "titulo" LIKE 'The %';
```

- Dado que hay un libro en la tabla cuyo nombre es "Pyre" o "Pire", podemos seleccionarlo ejecutando:

```sql
SELECT "titulo"
FROM "lista_larga"
WHERE "titulo" LIKE 'P_re';
```

Esta consulta tambien podria devolver titulos de libros como "Pore" o "Pure" si existieran en nuestra base de datos, porque `_` coincide con cualquier caracter individual.

### Preguntas

> ¿Podemos usar multiples simbolos `%` o `_` en una consulta?

- ¡Si, podemos! Ejemplo 1: Si quisieramos seleccionar libros cuyos titulos comienzan con "The" y tienen "love" en algun lugar del medio, podriamos ejecutar:

```sql
SELECT "titulo"
FROM "lista_larga"
WHERE "titulo" LIKE 'The%love%';
```

- Nota: Ningun libro de nuestra base de datos actual coincide con este patron, entonces esta consulta no devuelve nada.
- Ejemplo 2: Si supieramos que habia un libro en la tabla cuyo titulo comienza con "T" y tiene cuatro letras, podemos intentar encontrarlo ejecutando:

```sql
SELECT "titulo"
FROM "lista_larga"
WHERE "titulo" LIKE 'T____';
```

> ¿La comparacion de cadenas es sensible a mayusculas/minusculas en SQL?

- En PostgreSQL, la comparacion de cadenas con `LIKE` es por defecto sensible a mayusculas/minusculas **in**sensibles, mientras que la comparacion de cadenas con `=` es sensible a mayusculas/minusculas. (Nota que, en otros DBMS, ¡la configuracion de tu base de datos puede cambiar esto!)

---

## Rangos

- Tambien podemos usar los operadores `<`, `>`, `<=` y `>=` en nuestras condiciones para coincidir con un rango de valores. Por ejemplo, para seleccionar todos los libros en la lista larga entre los anos 2019 y 2022 (inclusive), podemos ejecutar:

```sql
SELECT "titulo", "autor"
FROM "lista_larga"
WHERE "anio" >= 2019 AND "anio" <= 2022;
```

- Otra forma de obtener los mismos resultados es usar las palabras clave `BETWEEN` y `AND` para especificar rangos inclusivos. Podemos ejecutar:

```sql
SELECT "titulo", "autor"
FROM "lista_larga"
WHERE "anio" BETWEEN 2019 AND 2022;
```

- Para seleccionar los libros que tienen una calificacion de 4.0 o superior, podemos ejecutar:

```sql
SELECT "titulo", "puntuacion"
FROM "lista_larga"
WHERE "puntuacion" > 4.0;
```

- Para limitar adicionalmente los libros seleccionados por numero de votos, y tener solo aquellos libros con al menos 10,000 votos, podemos ejecutar:

```sql
SELECT "titulo", "puntuacion", "votos"
FROM "lista_larga"
WHERE "puntuacion" > 4.0 AND "votos" > 10000;
```

- Para seleccionar los libros que tienen menos de 300 paginas, podemos ejecutar:

```sql
SELECT "titulo", "paginas"
FROM "lista_larga"
WHERE "paginas" < 300;
```

### Preguntas

> Para operadores de rango como `<` y `>`, ¿los valores en la base de datos tienen que ser enteros?

- No, los valores pueden ser enteros o numeros de punto flotante (es decir, numeros "decimales" o "reales"). Al crear una base de datos, hay formas de establecer estos tipos de datos para las columnas.

---

## ORDER BY

- La palabra clave `ORDER BY` nos permite organizar las filas devueltas en algun orden especificado.
- La siguiente consulta selecciona los 10 libros peores de nuestra base de datos por calificacion.

```sql
SELECT "titulo", "puntuacion"
FROM "lista_larga"
ORDER BY "puntuacion" LIMIT 10;
```

- Nota que obtenemos los 10 libros peores porque `ORDER BY` elige orden ascendente por defecto.
- En su lugar, para seleccionar los 10 mejores libros:

```sql
SELECT "titulo", "puntuacion"
FROM "lista_larga"
ORDER BY "puntuacion" DESC LIMIT 10;
```

Nota el uso de la palabra clave SQL `DESC` para especificar el orden descendente. `ASC` puede usarse para especificar explicitamente el orden ascendente.

- Para seleccionar los 10 mejores libros por calificacion y tambien incluir el numero de votos como desempatador, podemos ejecutar:

```sql
SELECT "titulo", "puntuacion", "votos"
FROM "lista_larga"
ORDER BY "puntuacion" DESC, "votos" DESC
LIMIT 10;
```

Nota que para cada columna en la clausula `ORDER BY`, especificamos orden ascendente o descendente.

### Preguntas

> Para ordenar libros por titulo alfabeticamente, ¿podemos usar `ORDER BY`?

- Si, podemos. La consulta seria:

```sql
SELECT "titulo"
FROM "lista_larga"
ORDER BY "titulo";
```

---

## Funciones de Agregacion

- `COUNT`, `AVG`, `MIN`, `MAX` y `SUM` se llaman funciones de agregacion y nos permiten realizar las operaciones correspondientes sobre multiples filas de datos. Por su propia naturaleza, cada una de las siguientes funciones de agregacion devolvera solo una unica salida: el valor agregado.
- Para encontrar la calificacion promedio de todos los libros en la base de datos:

```sql
SELECT AVG("puntuacion")
FROM "lista_larga";
```

- Para redondear la calificacion promedio a 2 decimales:

```sql
SELECT ROUND(AVG("puntuacion")::numeric, 2)
FROM "lista_larga";
```

- Para renombrar la columna en la cual se muestran los resultados:

```sql
SELECT ROUND(AVG("puntuacion")::numeric, 2) AS "puntuacion promedio"
FROM "lista_larga";
```

Nota el uso de la palabra clave SQL `AS` para renombrar columnas.

- Para seleccionar la calificacion maxima en la base de datos:

```sql
SELECT MAX("puntuacion")
FROM "lista_larga";
```

- Para seleccionar la calificacion minima en la base de datos:

```sql
SELECT MIN("puntuacion")
FROM "lista_larga";
```

- Para contar el numero total de votos en la base de datos:

```sql
SELECT SUM("votos")
FROM "lista_larga";
```

- Para contar el numero de libros en nuestra base de datos:

```sql
SELECT COUNT(*)
FROM "lista_larga";
```

  - Recuerda que usamos `*` para seleccionar cada fila y columna de la base de datos. En este caso, estamos intentando contar cada fila en la base de datos y por eso usamos el `*`.

- Para contar el numero de traductores:

```sql
SELECT COUNT("traductor")
FROM "lista_larga";
```

  - Observamos que el numero de traductores es menor que el numero de filas en la base de datos. Esto se debe a que la funcion `COUNT` no cuenta valores `NULL`.

- Para contar el numero de editoriales en la base de datos:

```sql
SELECT COUNT("editorial")
FROM "lista_larga";
```

- Al igual que con los traductores, esta consulta contara el numero de valores de editorial que no son `NULL`. Sin embargo, esto puede incluir duplicados. Otra palabra clave SQL, `DISTINCT`, puede usarse para asegurar que solo se cuenten valores distintos.

```sql
SELECT COUNT(DISTINCT "editorial")
FROM "lista_larga";
```

### Preguntas

> ¿Usar `MAX` con la columna de titulo te daria el titulo de libro mas largo?

- No, usar `MAX` con la columna de titulo te daria el titulo "mas grande" (o en este caso, el ultimo) alfabeticamente. De manera similar, `MIN` te dara el primer titulo alfabeticamente.

---

## Fin

- ¡Esto nos lleva a la conclusion de la Clase 0 sobre Consultas (Querying) en SQL! Para salir del prompt de psql, puedes escribir `\q` y esto te llevara de vuelta a la terminal regular.
- ¡Hasta la proxima vez!

---

**Fuente:** CS50 SQL - Lecture 0: Querying. Harvard University. https://cs50.harvard.edu/sql/notes/0/

Este material esta disponible bajo la licencia Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0).