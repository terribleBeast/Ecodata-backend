HOST ?= localhost
PORT ?= 8000
DB ?= D:\projects\EcoData\ecodata.db
LOGFILE_DB ?= D:\projects\EcoData\logfile
USERNAME_DB ?= "admin"
PASSWORD_DB ?= "admin"
SCHEMA ?= "D:\projects\EcoData\backend\ecodata_db_script.sql"

# stop_backend:
# 	uvicorn stop
stop_db:
	pg_ctl.exe -D $(DB) -c stop

run:
	uvicorn src.main:app --host $(HOST) --port $(PORT) --reload
run_db:
	pg_ctl.exe -D $(DB) -c $(COMMAND) -l $(LOGFILE_DB) -U $(USERNAME_DB) -P $(PASSWORD_DB)
init_db:
	pg_ctl.exe init -D $(DB) -U $(USERNAME_DB) -P $(PASSWORD_DB)
create_db:
	psql ecodata -U $(USERNAME_DB)  -f $(SCHEMA)
