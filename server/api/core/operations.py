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


# --------------------------------------------------------------------------------
# > Helpers
# --------------------------------------------------------------------------------
def ask_user_to_proceed():
    """
    Ask the user if he wants to proceed and returns a boolean answer
    :return: Whether to proceed
    :rtype: bool
    """
    print("Do you wish to proceed ? (y/n)")
    proceed = None
    while proceed is None:
        answer = input("").lower()
        if answer == "y":
            proceed = True
        elif answer == "n":
            print("Aborting operation...")
            proceed = False
        else:
            print("Invalid answer. Please type 'y' for yes or 'n' for no")
    return proceed


def run_tasks(tasks):
    """Runs tasks in order and stops early in one fails"""
    for task in tasks:
        print(">>> ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ <<<")
        success = task()
        if not success:
            break


# --------------------------------------------------------------------------------
# > Tasks
# --------------------------------------------------------------------------------
def create_super_user():
    """
    Creates a super user based on the settings data
    :return: The created super user
    :rtype: User
    """
    print("Creating a new super user")
    if hasattr(settings, "SUPER_USER"):
        user_data = settings.SUPER_USER
        username = user_data["username"]
        email = user_data["email"]
        password = user_data["password"]
        User.objects.create_superuser(username, email=email, password=password)
        print("Superuser created")
        return True
    else:
        print("Error: Could not create user")
        print("Please check the 'SUPER_USER' variable is correctly set in you settings")
        return False


def delete_migration_files():
    """
    Searches the 'migrations' folders and remove the migration files
    It does not remove the __init__.py file
    """
    print("Deleting migration files...")
    django_directory = os.getcwd()
    delete_count = 0
    for (dirpath, dirnames, filenames) in os.walk(django_directory):
        current_folder_name = os.path.basename(dirpath)
        if current_folder_name == "migrations":
            for filename in filenames:
                regex = r"^[0-9]{4}_.+\.py$"
                if re.search(regex, filename) is not None:
                    filepath = os.path.join(dirpath, filename)
                    os.remove(filepath)
                    print(f"Removed {filepath}")
                    delete_count += 1
    return True


def delete_sqlite3_database():
    """Finds and delete the sqlite3 database file"""
    print("Deleting the sqlite3 database")
    db_config = settings.DATABASES["default"]
    db_filepath = db_config["NAME"]
    _, file_ext = os.path.splitext(db_filepath)
    if file_ext == ".sqlite3":
        print(db_filepath)
        print("Database successfully deleted")
        return True
    else:
        print("Error: Database must be a sqlite3 file")
        return False


def make_and_do_migrations():
    """Wip"""
    # How to run command from command?
    pass


# --------------------------------------------------------------------------------
# > Operations
# --------------------------------------------------------------------------------
def reset_sqlite3_database(remake_migrations, create_user):
    """
    Removes and recreates the sqlite3 database of our application
    :param bool remake_migrations: Whether to delete and remake the migration files
    :param bool create_user: Whether to automatically create a super user
    """
    tasks = [delete_sqlite3_database]
    if remake_migrations:
        tasks.append(delete_migration_files)
    tasks.append(make_and_do_migrations)
    if create_user:
        tasks.append(create_super_user)
    run_tasks(tasks)


def remove_migrations():
    """Removes all the migration files of our custom apps"""
    run_tasks([delete_migration_files])


# TODO
#   auto input at 1 char
#   call django commands makemigrations migrate
#   how to handle "except all"
#   color printing
#   Operation
#       run
#       tasks
#       task 1 out of, clear, progress bar
#   Task
#       feedback
#       error
#       success
#       main function
#       name
