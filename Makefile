HOST ?= localhost
PORT ?= 8000
DB ?= D:\projects\EcoData\ecodata.db
LOGFILE_DB ?= D:\projects\EcoData\logfile
USERNAME_DB ?= "admin"
PASSWORD_DB ?= "admin"
SCHEMA ?= "D:\projects\EcoData\backend\ecodata_db_script.sql"
RUSTFS_ACCESS_KEY ?= "admin"
RUSTFS_SECRET_KEY ?= admin123456"
RUSTFS_VOLUME ?= "C:\rustfs-data"
# stop_backend:
# 	uvicorn stop
stop_db:
	pg_ctl.exe -D $(DB) -c stop

run:
	uvicorn src.main:app --host $(HOST) --port $(PORT) --reload
run_db:
	pg_ctl.exe -D $(DB) -c $(COMMAND) -l $(LOGFILE_DB) -U $(USERNAME_DB) -P $(PASSWORD_DB)
run_rustsf:
	"D:\Downloads\rustfs-windows-x86_64-latest\rustfs.exe" server $(RUSTFS_VOLUME)   --address ":9100" --console-address ":9101" --access-key $(RUSTFS_ACCESS_KEY)  --secret-key $(RUSTFS_SECRET_KEY)

init_db:
	pg_ctl.exe init -D $(DB) -U $(USERNAME_DB) -P $(PASSWORD_DB)
create_db:
	psql ecodata -U koval  -f $(SCHEMA)
