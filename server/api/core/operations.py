"""
Functions and utilities for our custom commands and operations
Split into 3 major categories:
    Helpers         Utility functions for actions and commands
    Task            Functions that perform one specific task and provide feedback in the console
    Operations      Functions used in actual Django commands. Call one or several actions
"""

# Built-in
import os
import re

# Django
from django.conf import settings
from django.contrib.auth.models import User
from django.core.management import call_command

# Personal
from jklib.django.commands.operations import Operation, OperationTask


# --------------------------------------------------------------------------------
# > Tasks
# --------------------------------------------------------------------------------
class TaskCreateSuperUser(OperationTask):
    """Creates a new super user based on the settings values"""

    name = "Superuser creation"

    def run(self):
        """Task job"""
        self.print_info("Fetching SUPER_USER data from settings")
        user_data = settings.SUPER_USER
        username = user_data["username"]
        email = user_data["email"]
        password = user_data["password"]
        self.print_info("Creating super user")
        User.objects.create_superuser(username, email=email, password=password)
        self.print_success(f"Super user '{username}' was created")


class TaskDeleteMigrationFiles(OperationTask):
    """
    Searches the 'migrations' folders and remove the migration files
    It does not remove the __init__.py file
    """

    name = "Migration files removal"

    def run(self):
        """Task job"""
        django_directory = os.getcwd()
        delete_count = 0
        self.print_info("Scanning files...")
        for (dirpath, dirnames, filenames) in os.walk(django_directory):
            current_folder_name = os.path.basename(dirpath)
            if current_folder_name == "migrations":
                for filename in filenames:
                    regex = r"^[0-9]{4}_.+\.py$"
                    if re.search(regex, filename) is not None:
                        filepath = os.path.join(dirpath, filename)
                        os.remove(filepath)
                        self.print_success(f"Removed {filepath}")
                        delete_count += 1


class TaskDeleteSqlite3Database(OperationTask):
    """Finds and removes the sqlite3 database file"""

    name = "Sqlite3 removal"

    def run(self):
        """Task job"""
        db_config = settings.DATABASES["default"]
        db_filepath = db_config["NAME"]
        _, file_ext = os.path.splitext(db_filepath)
        if file_ext == ".sqlite3":
            self.print_info("Removing sqlite3 database...")
            os.remove(db_filepath)
            self.print_success("Database successfully removed")
        else:
            raise Exception("Error: Database must be a sqlite3 file")


class TaskMakeAndDoMigrations(OperationTask):
    """Make and apply migrations using the classic Django commands"""

    name = "Migration update"

    def run(self):
        """Task job"""
        self.print_info("Making migrations files...")
        call_command("makemigrations")
        self.print_success("Migration files successfully updated")
        self.print_info("Applying migrations...")
        call_command("migrate")
        self.print_success("Migrations successfully applied")


# --------------------------------------------------------------------------------
# > Operations
# --------------------------------------------------------------------------------
class OperationRemoveMigrations(Operation):
    """Operation to remove migration files"""

    name = "Migration files removal"
    tasks = [TaskDeleteMigrationFiles]


class OperationResetSqlite3Database(Operation):
    """
    Operation that will perform the following tasks:
        Delete the sqlite3 database
        (Optional) Remove migration files
        Generate migration files
        Apply migrations
        (Optional) Create super user
    """

    name = "Sqlite3 Database Reset"

    def __init__(self, remake_migrations, create_user):
        """
        Adds additional tasks to delete migration files and create superuser based on the args
        :param bool remake_migrations: Whether to delete and remake the migration files
        :param bool create_user: Whether to automatically create a super user
        """
        tasks = [TaskDeleteSqlite3Database]
        if remake_migrations:
            tasks.append(TaskDeleteMigrationFiles)
        tasks.append(TaskMakeAndDoMigrations)
        if create_user:
            tasks.append(TaskCreateSuperUser)
        self.tasks = tasks
