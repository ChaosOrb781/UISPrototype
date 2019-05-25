@echo off

"C:\Program Files\PostgreSQL\11\bin\psql.exe" -U postgres -f database.sql
ECHO "Setting up database and schema..."
"C:\Program Files\PostgreSQL\11\bin\psql.exe" -U postgres -d prototype -f schema.sql
ECHO "Inserting dummy data..."
"C:\Program Files\PostgreSQL\11\bin\psql.exe" -U postgres -d prototype -f schema_insert.sql
ECHO "Done."

PAUSE