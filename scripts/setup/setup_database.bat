@echo off

"C:\Program Files\PostgreSQL\17\bin\createdb.exe" teacher_chatbot_database

"C:\Program Files\PostgreSQL\17\bin\createuser.exe" -P -e teacher_chatbot_user

"C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE teacher_chatbot_database TO teacher_chatbot_user;"

"C:\Program Files\PostgreSQL\17\bin\psql.exe" -U teacher_chatbot_user -d teacher_chatbot_database -h localhost -f database_dump.sql