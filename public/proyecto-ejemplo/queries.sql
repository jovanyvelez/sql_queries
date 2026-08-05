-- Buscar todas las entregas dado el nombre y apellido del estudiante
SELECT *
FROM "submissions"
WHERE "student_id" IN (
    SELECT "id"
    FROM "students"
    WHERE "first_name" = 'Yuliia'
    AND "last_name" = 'Zhukovets'
);

-- Buscar todas las entregas dado el nombre de usuario de GitHub del estudiante
SELECT *
FROM "submissions"
WHERE "student_id" = (
    SELECT "id"
    FROM "students"
    WHERE "github_username" = 'CarterZenke'
);

-- Buscar todas las entregas para un problema dado
SELECT * 
FROM "submissions"
WHERE "problem_id" = (
    SELECT "id"
    FROM "problems"
    WHERE "name" = 'Packages'
);

-- Agregar un nuevo estudiante
INSERT INTO "students" ("first_name", "last_name", "github_username")
VALUES ('Carter', 'Zenke', 'CarterZenke');

-- Agregar un nuevo instructor
INSERT INTO "instructors" ("first_name", "last_name")
VALUES ('Carter', 'Zenke');

-- Agregar una nueva entrega
INSERT INTO "submissions" ("student_id", "problem_id", "submission_path", "correctness")
VALUES (1, 1, '/submissions/cyberchase/1/', 1.0);
