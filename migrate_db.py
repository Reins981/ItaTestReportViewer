import sys
import os
import subprocess
import shutil
from app import app

MIGRATE_DIR = "migrations"


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
