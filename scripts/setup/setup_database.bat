@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

REM === CONFIGURATION ===
SET PGBIN="C:\Program Files\PostgreSQL\17\bin"
SET DBNAME=teacher_chatbot_database
SET DBUSER=teacher_chatbot_user
SET DBPASS=team4ai
SET PGHOST=localhost
SET DUMPFILE=database_dump.sql

REM === Drop database if it exists ===
%PGBIN%\psql.exe -U postgres -h %PGHOST% -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '%DBNAME%' AND pid <> pg_backend_pid();"
%PGBIN%\psql.exe -U postgres -h %PGHOST% -c "DROP DATABASE IF EXISTS %DBNAME%;"

REM === Drop and recreate user ===
%PGBIN%\psql.exe -U postgres -h %PGHOST% -c "DROP USER IF EXISTS %DBUSER%;"
%PGBIN%\psql.exe -U postgres -h %PGHOST% -c "CREATE USER %DBUSER% WITH PASSWORD '%DBPASS%';"

REM === Create database ===
%PGBIN%\createdb.exe -U postgres -h %PGHOST% -O %DBUSER% %DBNAME%

REM === Grant privileges ===
%PGBIN%\psql.exe -U postgres -h %PGHOST% -c "GRANT ALL PRIVILEGES ON DATABASE %DBNAME% TO %DBUSER%;"

REM === Load dump file if it exists ===
IF EXIST %DUMPFILE% (
    echo Loading database dump...
    %PGBIN%\psql.exe -U %DBUSER% -h %PGHOST% -d %DBNAME% -f %DUMPFILE%
    echo Database dump loaded successfully.
) ELSE (
    echo Warning: %DUMPFILE% not found. Creating empty database.
)

echo Database setup completed successfully.
ENDLOCAL
pause
