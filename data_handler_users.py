import os
import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor

import database_common
import util


@database_common.connection_handler
def add_user(cursor, email, password):
    cursor.execute(
        sql.SQL("""INSERT INTO {table} ({col_1}, {col_2}, {col_3})
                    VALUES (now()::timestamp(0), %(email)s, %(password)s)"""
                ).format(
                        table=sql.Identifier('users'),
                        col_1=sql.Identifier('registration_time'),
                        col_2=sql.Identifier('email'),
                        col_3=sql.Identifier('password')
        ), {
            'email': email,
            'password': util.hash_password(password),
        }
    )


def is_valid_login(email, password):
    try:
        db_password = get_user_password(email)
        print (db_password)
        return util.verify_password(password, db_password)
    except psycopg2.Error:
        return


@database_common.connection_handler
def get_user_password(cursor, email):
    cursor.execute(
        sql.SQL(
            """SELECT password FROM users
            WHERE email = %(email)s
            """
        ),
        {'email': email}
    )
    return cursor.fetchone()['password']
