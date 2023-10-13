import sys
import os
import json
import subprocess
import shutil
from app import app, CONFIG_FILE

MIGRATE_DIR = "migrations"


def set_database(database_path):

    with open(CONFIG_FILE, 'r') as f:
        config_data = json.load(f)

    # Set the new database path
    config_data['database_path'] = database_path

    with open(CONFIG_FILE, 'w') as f:
        json.dump(config_data, f, indent=4)

    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_path}'
    print(f"Database path updated to: {database_path}")

    return database_path


def migrate_db():
    if os.path.exists(MIGRATE_DIR) and os.path.isdir(MIGRATE_DIR):
        print("Migration environment exists already, removing it...")
        shutil.rmtree(MIGRATE_DIR)

    # Command 1: Initialize the Flask database
    init_command = [sys.executable, "-m", "flask", "db", "init"]
    subprocess.run(init_command, shell=True)

    # Command 2: Create a migration with a description
    migrate_command = [sys.executable, "-m", "flask", "db", "migrate", "-m", "Migrate db"]
    subprocess.run(migrate_command, shell=True)

    # Command 3: Apply the migration
    upgrade_command = [sys.executable, "-m", "flask", "db", "upgrade"]
    subprocess.run(upgrade_command, shell=True)


if __name__ == '__main__':
    try:
        if len(sys.argv) > 1:
            database = sys.argv[1]
            database_p = set_database(database)
        migrate_db()
    except Exception as e:
        print(f"An error occurred: {str(e)}")
