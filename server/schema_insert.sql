DELETE FROM posts;
DELETE FROM threads;
DELETE FROM patients;
DELETE FROM employees;
DELETE FROM users;
DELETE FROM medical;

INSERT INTO public.users(CPR, firstname, lastname, password, address) VALUES ('0206874571', 'Mikkel', 'P&oslash;ulsen', '1', 'Cancergade 100');
INSERT INTO public.users(CPR, firstname, lastname, password, address) VALUES ('0807650909', 'Tobias', 'Florrr', '12', 'Amaliegade 1');
INSERT INTO public.users(CPR, firstname, lastname, password, address) VALUES ('1212121212', 'Mads', 'Paludan', '123', 'r&oslash;dstr&oslash;mpevej 2');
INSERT INTO public.users(CPR, firstname, lastname, password, address) VALUES ('1312145152', 'Jonas', 'Swork', '1234', 'matronevej 67');
INSERT INTO public.users(CPR, firstname, lastname, password, address) VALUES ('0112894555', 'Gunnar', 'Nielsen', '12345', 'Paludan Parkvej 69');
INSERT INTO public.users(CPR, firstname, lastname, password, address) VALUES ('0711012286', 'Mickey', 'Mouse', '123456', 'Garden Square 666, Hell');
INSERT INTO public.users(CPR, firstname, lastname, password, address) VALUES ('1007889934', 'Mynte', 'Olsen', '1234567', 'Nightmare Street 7');
INSERT INTO public.users(CPR, firstname, lastname, password, address) VALUES ('2412199955', 'Oluf', 'Sand', '12345678', 'HC Andersens Boulevard 1');

INSERT INTO public.patients(CPR, journal, process_id) VALUES ('0206874571', 1, 1);
INSERT INTO public.patients(CPR, journal, process_id) VALUES ('0807650909', 2, 2);
INSERT INTO public.patients(CPR, journal, process_id) VALUES ('1212121212', 3, 3);
INSERT INTO public.patients(CPR, journal, process_id) VALUES ('1312145152', 4, 4);
INSERT INTO public.patients(CPR, journal, process_id) VALUES ('0112894555', 5, 5);
INSERT INTO public.patients(CPR, journal, process_id) VALUES ('0711012286', 6, 6);

INSERT INTO public.employees(CPR, specialization, temp, privilege, works_at) VALUES ('1007889934', 'Sygeplejerske', FALSE, 1, 0);
INSERT INTO public.employees(CPR, specialization, temp, privilege, works_at) VALUES ('2412199955', 'Overl&aelig;ge', FALSE, 2, 0);

INSERT INTO public.threads(CPR, header, content, created_date) VALUES ('0206874571', 'wtf is this forum', 'pls someone eli5 why do we need dis shiet', '2018-06-01');
INSERT INTO public.threads(CPR, header, content) VALUES ('1212121212', 'diarrhea and anal pain', 'send halp plx');

INSERT INTO public.posts(tid, CPR, content, created_date) VALUES ((SELECT id FROM threads WHERE CPR='0206874571'), '1007889934', 'Ved anale smerter anbefaler vi en n&aelig;rmere unders&oslash;gelse hos egen l&aelig;ge.', '2018-09-03');
INSERT INTO public.posts(tid, CPR, content, created_date) VALUES ((SELECT id FROM threads WHERE CPR='0206874571'), '2412199955', 'Du b&oslash;r f&oslash;rst s&oslash;ge egen l&aelig;ge, som dern&aelig;st vil sende dig videre i systemet.', '2018-10-01');
INSERT INTO public.posts(tid, CPR, content, created_date) VALUES ((SELECT id FROM threads WHERE CPR='1212121212'), '1007889934','Jeg vil lige tilf&oslash;je, at k&oslash;nsskifteoperationer er v&aelig;sentligt billigere i japan.', '2018-11-07');
INSERT INTO public.posts(tid, CPR, content, created_date, modified_date) VALUES ((SELECT id FROM threads WHERE CPR='0206874571'), '2412199955', 'F&aring; dig en s&oslash;dere k&aelig;reste.', '2018-05-11', '2018-05-11');
INSERT INTO public.posts(tid, CPR, content, created_date) VALUES ((SELECT id FROM threads WHERE CPR='1212121212'), '1007889934','Du kan ogs&aring; overveje en cyborg operation for kun $999999999999.99', '2018-11-08');

INSERT INTO public.medical(id, name, latin_name, description, created_by, created_date) VALUES (1, 'Accessio', 'Ceserio', 'Epileptisk anfald/kramper', 'Doktor Hansen', '2018-10-01');
INSERT INTO public.medical(id, name, latin_name, description, created_by, created_date) VALUES (2, 'Testistorsion', 'EvenMoreTest', 'Noget du ikke vil bryde dig om', 'Doktor Hansen', '2018-10-01');

COMMIT;