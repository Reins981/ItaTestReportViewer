from cx_Freeze import setup, Executable
import os

# Define the list of Executables (your main script)
executables = [Executable(
    script="run.py",  # Replace with the name of your main script
    base="Console",  # Use "Console" for command-line applications
)]

# Additional options, including packages and include files
build_options = {
    "packages": ["app"],
    "excludes": ["tkinter"],  # Exclude tkinter if not needed
    "include_files": ["app/__init__.py",
                      "app/models.py",
                      "app/routes.py",
                      "migrate_db.py"],  # Include any data files
    "includes": ["flask",
                 "flask_sqlalchemy",
                 "flask_migrate",
                 "os",
                 "sqlalchemy.dialects.sqlite",
                 "json",
                 "re",
                 "urllib",
                 "sqlalchemy"],  # Include the SQLite module
}

# Create setup configuration
setup(
    name="ItaReportViewer",
    version="1.0",
    description="Ita Report Viewer Web Application",
    executables=executables,
    options={"build_exe": build_options},
)
