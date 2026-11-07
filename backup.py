"""
This file is used to backup the databases in both sql and sqlite3 format
"""
from zipfile import ZipFile
import os, sqlite3, shutil, tempfile
from datetime import datetime
TARGET_TEMP_DIR = f"backup-{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"


def backup_db(target_database_name: str):
    """
    This will backup the database
    """
    target_database_file_path = os.path.join(TARGET_TEMP_DIR, target_database_name)
    target_sql_file_path = os.path.join(TARGET_TEMP_DIR, f"{target_database_name}.sql")
    with sqlite3.connect(target_database_name) as source_connection, sqlite3.connect(target_database_file_path) as target_connection:
        source_connection.backup(target_connection)
    os.system(f"sqlite3 {target_database_file_path} .dump > {target_sql_file_path}")
    return target_database_file_path, target_sql_file_path
    
def backup():
    TARGET_FILENAME = f"backup-{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.zip"
    os.mkdir(TARGET_TEMP_DIR)
    main_db, main_sql = backup_db("data.db")
    cache_db, cache_sql = backup_db("articles.db")
    logs_db, logs_sql = backup_db("logs.db")
    with ZipFile(TARGET_FILENAME , "w") as zip_file:
        zip_file.write(main_db)
        zip_file.write(main_sql)
        zip_file.write(cache_db)
        zip_file.write(cache_sql)
        zip_file.write(logs_db)
        zip_file.write(logs_sql)
    shutil.rmtree(TARGET_TEMP_DIR)
    return TARGET_FILENAME
if __name__ == "__main__":
    backup()

    

