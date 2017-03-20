"""
 __          __     _____  _   _ _____ _   _  _____
 \ \        / /\   |  __ \| \ | |_   _| \ | |/ ____|
  \ \  /\  / /  \  | |__) |  \| | | | |  \| | |  __
   \ \/  \/ / /\ \ |  _  /| . ` | | | | . ` | | |_ |
    \  /\  / ____ \| | \ \| |\  |_| |_| |\  | |__| |
     \/  \/_/    \_\_|  \_\_| \_|_____|_| \_|\_____|

This fab file was created purely to make devs lives easier
and less repetitive.

Therefore PLEASE DO NOT USE the functions on this file
in a production environment, using this fab file in production
might cause irreversable issues.
"""
import sys
sys.path.insert(0, sys.path[0])
from fabric.api import local, env, hide, settings
from fabric.contrib import django

django.settings_module('searchlens.settings.development')
from django.conf import settings as searchlens_settings


env.host_string = 'localhost'


def install_postgres():
    with settings(warn_only=True):
        result = local('psql --version')
        if result.failed:
            print('Installing PostgreSQL')
            local('sudo apt-get install postgresql postgresql-contrib -y')


def uninstall_postgres():
    with settings(warn_only=True):
        result = local('sudo service postgresql stop')
        if not result.failed:
            local('sudo apt-get purge postgresql -y')
            local('sudo apt-get purge "postgresql-*" -y')
            local('sudo apt-get autoremove -y')


def postgres_user_account_setup():
    db_user = env.user
    db_name = env.user
    user_roles = 'SUPERUSER CREATEDB CREATEROLE REPLICATION'

    with hide('running', 'warnings'), settings(warn_only=True):
        result = local('sudo -u postgres psql -c "CREATE USER %s WITH %s;"' %
                       (db_user, user_roles))

        if not result.failed:
            local('sudo -u postgres psql -c '
                  '"CREATE DATABASE  %s WITH OWNER %s;"' %
                  (db_user, db_name))


def postgres_drop_account_setup():
    db_user = env.user
    db_name = env.user

    with hide('running', 'warnings'), settings(warn_only=True):
        local('sudo -u postgres dropdb %s;' % (db_name))
        local('sudo -u postgres dropuser %s;' % (db_user))


def create_database_user():
    db_user = searchlens_settings.DATABASES['default']['USER']
    db_psswd = searchlens_settings.DATABASES['default']['PASSWORD']

    with hide('running', 'warnings'), settings(warn_only=True):
        local('psql -c "CREATE USER %s WITH PASSWORD \'%s\';"' %
              (db_user, db_psswd))


def create_database():
    db_user = searchlens_settings.DATABASES['default']['USER']
    db_name = searchlens_settings.DATABASES['default']['NAME']

    with hide('running', 'warnings'), settings(warn_only=True):
        local(
            'psql -c "CREATE DATABASE %s WITH OWNER %s;"' % (db_name, db_user))


def drop_database():
    """
    Drops the user database. Needs to be run before drop_user()
    """
    db_name = searchlens_settings.DATABASES['default']['NAME']

    with hide('running', 'warnings'), settings(warn_only=True):
        local('psql -c "DROP DATABASE IF EXISTS %s;"' % (db_name))


def drop_user():
    """
    Drops the user role. Needs to be run after drop_database().
    Needs to be run with sudo privileges.
    """
    db_user = searchlens_settings.DATABASES['default']['USER']

    with hide('running', 'warnings'), settings(warn_only=True):
        local('psql -c "DROP USER IF EXISTS %s;"' % (db_user))


def searchlens_syncdb():
    local('./manage.py syncdb')


def searchlens_migrate():
    local('./manage.py migrate')


def postgres_setup():
    install_postgres()
    postgres_user_account_setup()


def searchlens_database_setup():
    create_database_user()
    create_database()


def searchlens_drop_database():
    drop_database()
    drop_user()


def searchlens_setup():
    postgres_setup()
    searchlens_database_setup()
    searchlens_syncdb()
    searchlens_migrate()


def postgres_purge():
    postgres_drop_account_setup()
    uninstall_postgres()

