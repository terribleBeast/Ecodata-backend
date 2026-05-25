HOST ?= localhost
PORT ?= 8000
DB ?= D:\projects\EcoData\ecodata.db
LOGFILE_DB ?= D:\projects\EcoData\logfile

run: run_db run_backend COMMAND=start
# stop:

# stop_backend:
# 	uvicorn stop
stop_db:
	pg_ctl.exe -D $(DB) -c stop

run_bd:
	uvicorn src.main:app --host $(HOST) --port $(PORT)

run_backend:
	uvicorn src.main:app --host $(HOST) --port $(PORT) --reload
run_db:
	pg_ctl.exe -D $(DB) -c $(COMMAND) -l $(LOGFILE_DB)
