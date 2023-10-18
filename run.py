import sys
import json
from app import app, CONFIG_FILE


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


if __name__ == '__main__':
    try:
        if len(sys.argv) > 1:
            database = sys.argv[1]
            database_p = set_database(database)
        app.run(debug=True)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        input("Press Enter to exit...")
