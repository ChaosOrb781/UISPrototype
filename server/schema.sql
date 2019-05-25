\set AUTOCOMMIT off
\echo :AUTOCOMMIT

DROP TABLE IF EXISTS posts;
DROP TABLE IF EXISTS threads;
DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS employees_backup;
DROP TABLE IF EXISTS patients;
DROP TABLE IF EXISTS patients_backup;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS users_backup;

CREATE TABLE IF NOT EXISTS users(
	CPR char(10) PRIMARY KEY,
	firstname varchar(120),
	lastname varchar(120),
	password varchar(120) NOT NULL,
	address text DEFAULT 'Adresse ikke sat',
	created_date timestamp DEFAULT CURRENT_TIMESTAMP,
	last_online_date timestamp DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS users_backup(
	CPR char(10) PRIMARY KEY,
	firstname varchar(120) NOT NULL,
	lastname varchar(120) NOT NULL,
	password varchar(120) NOT NULL,
	address text DEFAULT 'Adresse ikke sat',
	created_date timestamp DEFAULT CURRENT_TIMESTAMP,
	last_online_date timestamp DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS employees(
	CPR char(10) PRIMARY KEY,
	specialization varchar(100) NOT NULL,
	temp boolean DEFAULT TRUE,
	privilege integer DEFAULT 0,
	works_at integer NOT NULL,
	FOREIGN KEY (CPR) REFERENCES users(CPR)
  --FOREIGN KEY (works_at) REFERENCES departments(id)
);

CREATE TABLE IF NOT EXISTS employees_backup(
	CPR char(10) PRIMARY KEY,
	specialization varchar(100) NOT NULL,
	temp boolean DEFAULT TRUE,
	privilege integer DEFAULT 0,
	works_at integer NOT NULL,
	FOREIGN KEY (CPR) REFERENCES users(CPR)
  --FOREIGN KEY (works_at) REFERENCES departments(id)
);

CREATE TABLE IF NOT EXISTS patients(
	CPR char(10) PRIMARY KEY,
	journal integer,
	process_id integer,
	FOREIGN KEY (CPR) REFERENCES users(CPR)
	--FOREIGN KEY (journal) REFERENCES journals(id)
	--FOREIGN KEY (process_id) REFERENCES process(id)
);

CREATE TABLE IF NOT EXISTS patients_backup(
	CPR char(10) PRIMARY KEY,
	journal integer,
	process_id integer,
	FOREIGN KEY (CPR) REFERENCES users(CPR)
	--FOREIGN KEY (journal) REFERENCES journals(id)
	--FOREIGN KEY (process_id) REFERENCES process(id)
);

CREATE TABLE IF NOT EXISTS threads(
	id SERIAL PRIMARY KEY,
	CPR char(10) NOT NULL,
	header varchar(100) NOT NULL,
	content text NOT NULL,
	created_date timestamp DEFAULT CURRENT_TIMESTAMP,
	is_open boolean DEFAULT TRUE,
	FOREIGN KEY (CPR) REFERENCES users(CPR)
);

CREATE TABLE IF NOT EXISTS posts(
	id SERIAL PRIMARY KEY,
	tid integer NOT NULL,
	CPR char(10) NOT NULL,
  content text NOT NULL,
	created_date timestamp DEFAULT CURRENT_TIMESTAMP,
	modified_date timestamp DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY (tid) REFERENCES threads(id),
	FOREIGN KEY (CPR) REFERENCES users(CPR)
);

DROP TRIGGER IF EXISTS insert_user ON users;
DROP TRIGGER IF EXISTS insert_patient ON patients;
DROP TRIGGER IF EXISTS insert_employee ON employees;

CREATE OR REPLACE FUNCTION update_userbackup() RETURNS trigger AS $update_userbackup$
BEGIN
	NEW.CPR = OLD.CPR;
	IF (OLD.firstname IS DISTINCT FROM NEW.firstname) THEN
		EXECUTE CONCAT('UPDATE users_backup SET firstname = ', NEW.firstname, 'WHERE CPR = ', OLD.CPR); 
	END IF;
	IF (OLD.lastname IS DISTINCT FROM NEW.lastname) THEN
		EXECUTE CONCAT('UPDATE users_backup SET lastname = ', NEW.lastname, 'WHERE CPR = ', OLD.CPR); 
	END IF;
	IF (OLD.password IS DISTINCT FROM NEW.password) THEN
		EXECUTE CONCAT('UPDATE users_backup SET password = ', NEW.password, 'WHERE CPR = ', OLD.CPR); 
	END IF;
	IF (OLD.address IS DISTINCT FROM NEW.address) THEN
		EXECUTE CONCAT('UPDATE users_backup SET address = ', NEW.address, 'WHERE CPR = ', OLD.CPR); 
	END IF;
	RETURN NEW;
END;
$update_userbackup$ LANGUAGE plpgsql;

CREATE TRIGGER insert_user AFTER UPDATE ON users
FOR ROW
	WHEN (OLD.* IS DISTINCT FROM NEW.*)
	EXECUTE PROCEDURE update_userbackup();

COMMIT;
