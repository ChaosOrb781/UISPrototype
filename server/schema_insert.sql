DELETE FROM posts;
DELETE FROM threads;
DELETE FROM patients;
DELETE FROM employees;
DELETE FROM users;
DELETE FROM medical;

INSERT INTO public.users(CPR, firstname, lastname, password, address) VALUES (0206874571, 'Mikkel', 'Poulsen', '1', 'Cancergade 100');
INSERT INTO public.users(CPR, firstname, lastname, password, address) VALUES (0807650909, 'Tobias', 'Florrr', '12', 'Amaliegade 1');
INSERT INTO public.users(CPR, firstname, lastname, password, address) VALUES (1212121212, 'Mads', 'Paludan', '123', 'rødstrømpevej 2');
INSERT INTO public.users(CPR, firstname, lastname, password, address) VALUES (1312145152, 'Jonas', 'Swork', '1234', 'matronevej 67');
INSERT INTO public.users(CPR, firstname, lastname, password, address) VALUES (0112894555, 'Gunnar', 'Nielsen', '12345', 'Paludan Parkvej 69');
INSERT INTO public.users(CPR, firstname, lastname, password, address) VALUES (0711012286, 'Mickey', 'Mouse', '123456', 'Garden Square 666, Hell');
INSERT INTO public.users(CPR, firstname, lastname, password, address) VALUES (1007889934, 'Mynte', 'Olsen', '1234567', 'Nightmare Street 7');
INSERT INTO public.users(CPR, firstname, lastname, password, address) VALUES (2412199955, 'Oluf', 'Sand', '12345678', 'HC Andersens Boulevard 1');

INSERT INTO public.patients(CPR, journal, process_id) VALUES (0206874571, 1, 1);
INSERT INTO public.patients(CPR, journal, process_id) VALUES (0807650909, 2, 2);
INSERT INTO public.patients(CPR, journal, process_id) VALUES (1212121212, 3, 3);
INSERT INTO public.patients(CPR, journal, process_id) VALUES (1312145152, 4, 4);
INSERT INTO public.patients(CPR, journal, process_id) VALUES (0112894555, 5, 5);
INSERT INTO public.patients(CPR, journal, process_id) VALUES (0711012286, 6, 6);

INSERT INTO public.employees(CPR, specialization, temp, privilege, works_at) VALUES (1007889934, 'Sygeplejerske', FALSE, 1, 0);
INSERT INTO public.employees(CPR, specialization, temp, privilege, works_at) VALUES (2412199955, 'Overlæge', FALSE, 2, 0);

INSERT INTO public.threads(id, CPR, header, content, created_date) VALUES (1, 0206874571, 'wtf is this forum??', 'pls someone eli5 why do we need dis shiet??', '2018-06-01');
INSERT INTO public.threads(id, CPR, header, content) VALUES (2, 1212121212, 'diarrhea and anal pain', 'send halp plx');

INSERT INTO public.posts(id, tid, CPR, content, created_date) VALUES (1, 1, 1007889934, 'Ved anale smerter anbefaler vi en nærmere undersøgelse hos egen læge.', '2018-09-03');
INSERT INTO public.posts(id, tid, CPR, content, created_date) VALUES (2, 1, 2412199955, 'Du bør først søge egen læge, som dernæst vil sende dig videre i systemet.', '2018-10-01');
INSERT INTO public.posts(id, tid, CPR, content, created_date) VALUES (3, 2, 1007889934,'Jeg vil lige tilføje, at kønsskifteoperationer er væsentligt billigere i japan.', '2018-11-07');
INSERT INTO public.posts(id, tid, CPR, content, created_date, modified_date) VALUES (4, 1, 2412199955, 'Få dig en sødere kæreste.', '2018-05-11', '2018-05-11');
INSERT INTO public.posts(id, tid, CPR, content, created_date) VALUES (5, 2, 1007889934,'Du kan også overveje en cyborg operation for kun $999999999999.99', '2018-11-08');

INSERT INTO public.medical(id, name, latin_name, description, created_by, created_date) VALUES (1, 'Accessio', 'Ceserio', 'Epileptisk anfald/kramper', 'Doktor Hansen', '2018-10-01');
INSERT INTO public.medical(id, name, latin_name, description, created_by, created_date) VALUES (2, 'Testistorsion', 'EvenMoreTest', 'Noget du ikke vil bryde dig om', 'Doktor Hansen', '2018-10-01');

COMMIT;