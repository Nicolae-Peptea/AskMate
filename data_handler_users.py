import os
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
                        col_1=sql.Identifier('"registration_time"'),
                        col_2=sql.Identifier('email'),
                        col_3=sql.Identifier('password')
        ), {
            'email': email,
            'password': util.hash_password(password),
        }
    )


@database_common.connection_handler
def add_question(cursor: RealDictCursor, new_entry: dict):
    adding = """INSERT INTO question ("submission_time","title","message","image","view_number","vote_number")
                VALUES (now()::timestamp(0), %(title)s, %(message)s, %(image)s, 0, 0)
                """
    cursor.execute(adding, {
        'title': new_entry['title'],
        'message': new_entry['message'],
        'image': new_entry.get('image', None),
    })
