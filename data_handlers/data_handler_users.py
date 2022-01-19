from psycopg2 import sql

import data_handlers.database_common as database_common
import data_handlers.util as util


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
        return util.verify_password(password, db_password)
    except TypeError:
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


@database_common.connection_handler
def get_user_id(cursor, email):
    cursor.execute(
        sql.SQL(
            """SELECT id FROM users
            WHERE email = %(email)s
            """),
        {'email': email})

    return cursor.fetchone()['id']


@database_common.connection_handler
def get_users_details(cursor):
    script = """
        DROP TABLE IF EXISTS final;

        CREATE TEMPORARY TABLE final (
            user_id int,
            user_name text,
            registration_time timestamp without time zone,
            question_number int,
            answer_number int,
            comments_number int,
            reputation int
        );

        INSERT INTO final (user_id, user_name, registration_time, reputation)
        SELECT id, email, registration_time, reputation FROM users;

        UPDATE final f SET question_number=q.number_of_questions
        FROM (SELECT count(id) AS number_of_questions, user_id from question GROUP BY user_id) q
        WHERE f.user_id = q.user_id;

        UPDATE final f SET answer_number=a.number_of_answers
        FROM (SELECT count(id) AS number_of_answers, user_id from answer GROUP BY user_id) a
        WHERE f.user_id = a.user_id;

        UPDATE final f SET comments_number=c.number_of_comments
        FROM (SELECT count(id) AS number_of_comments, user_id from comment GROUP BY user_id) c
        WHERE f.user_id = c.user_id;

        SELECT user_id, user_name, registration_time,
            coalesce(question_number, 0) AS question_number,
            coalesce(answer_number, 0) AS answer_number,
            coalesce(comments_number, 0) AS comments_number,
            coalesce(reputation, 0) AS reputation
        FROM final;
    """
    cursor.execute(script)
    results = cursor.fetchall()
    cursor.execute("DROP TABLE IF EXISTS final;")
    
    return results


@database_common.connection_handler
def get_user_statistics(cursor, user_id):
    script = """
        DROP TABLE IF EXISTS final;

        CREATE TEMPORARY TABLE final (
            user_id int,
            user_name text,
            registration_time timestamp without time zone,
            question_number int,
            answer_number int,
            comments_number int,
            reputation int
        );

        INSERT INTO final (user_id, user_name, registration_time, reputation)
        SELECT id, email, registration_time, reputation FROM users;

        UPDATE final f SET question_number=q.number_of_questions
        FROM (SELECT count(id) AS number_of_questions, user_id from question GROUP BY user_id) q
        WHERE f.user_id = q.user_id;

        UPDATE final f SET answer_number=a.number_of_answers
        FROM (SELECT count(id) AS number_of_answers, user_id from answer GROUP BY user_id) a
        WHERE f.user_id = a.user_id;

        UPDATE final f SET comments_number=c.number_of_comments
        FROM (SELECT count(id) AS number_of_comments, user_id from comment GROUP BY user_id) c
        WHERE f.user_id = c.user_id;

        SELECT user_id, user_name, registration_time,
            coalesce(question_number, 0) AS question_number,
            coalesce(answer_number, 0) AS answer_number,
            coalesce(comments_number, 0) AS comments_number,
            coalesce(reputation, 0) AS reputation
        FROM final
        WHERE user_id = %(user_id)s;
    """
    cursor.execute(script, {'user_id': user_id}) 
    results = cursor.fetchall()
    cursor.execute("DROP TABLE IF EXISTS final;")
    
    return results


@database_common.connection_handler
def change_reputation_based_on_question(cursor, value, entry_id):
    cursor.execute(
        sql.SQL(
            """
            update users
            set reputation = reputation + %(change)s
            where users.email = (
            select users.email from users
            join question q on users.id = q.user_id
            WHERE q.id = %(entry_id)s)
            """
        ),
        {
            'change': value,
            'entry_id': entry_id,
        }
    )


@database_common.connection_handler
def change_reputation_based_on_answer(cursor, value, entry_id):
    cursor.execute(
        sql.SQL(
            """
            update users
            set reputation = reputation + %(change)s
            where users.email = (
            select users.email from users
            join answer a on users.id = a.user_id
            WHERE a.id = %(entry_id)s)
            """
        ),
        {
            'change': value,
            'entry_id': entry_id,
        }
    )
