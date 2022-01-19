import os
from psycopg2 import sql
from psycopg2.extras import RealDictCursor

import data_handlers.database_common as database_common
import data_handlers.data_handler_users as data_handler_users
import uuid


@database_common.connection_handler
def get_answer(cursor: RealDictCursor, answer_id: int):
    query = """SELECT * FROM answer
                WHERE id = %(answer_id)s
            """
    
    cursor.execute(query, {"answer_id": answer_id})
    
    return dict(cursor.fetchone())


@database_common.connection_handler
def get_answers_for_question(cursor: RealDictCursor, question_id: int):
    query = """
                SELECT
                    a.uuid,
                    a.id,
                    a.submission_time,
                    a.vote_number,
                    a.question_id,
                    a.message,
                    a.image,
                    a.accepted_by_user,
                    u.email,
                    u.id AS user_id
                FROM answer a
                JOIN users u ON u.id = a.user_id
                WHERE a.question_id = %(question_id)s
                ORDER BY vote_number DESC
                """
    
    cursor.execute(query, {"question_id": question_id})
    
    return cursor.fetchall()


@database_common.connection_handler
def get_last_added_answer_id(cursor: RealDictCursor):
    cursor.execute('SELECT MAX(id) FROM answer')
    return cursor.fetchone()['max']


@database_common.connection_handler
def qet_answers_by_user_id(cursor, user_id: int):
    cursor.execute(
        sql.SQL(
            """
            SELECT {col_1}, {col_2}
            FROM {table}
            WHERE {col_3} = %(user_id)s
            """
        ).format(
            table=sql.Identifier('answer'),
            col_1=sql.Identifier('message'),
            col_2=sql.Identifier('question_id'),
            col_3=sql.Identifier('user_id'),
        ),
        {
           'user_id': user_id,
        }
    )
    return cursor.fetchall()


@database_common.connection_handler
def get_image_names_for_answers(cursor: RealDictCursor, entry_id: int):
    query = """
       SELECT image
           FROM answer
       WHERE id= %(entry_id)s
       """
    cursor.execute(query, {'entry_id': entry_id})
    
    return [value for e in cursor.fetchall() for key, value in e.items() if value]


@database_common.connection_handler
def add_answer(cursor: RealDictCursor, new_entry: dict, question_id: int, email: str):
    adding = """INSERT INTO answer (uuid, user_id, submission_time, question_id, message, image)
                VALUES (%(uuid)s, %(user_id)s ,now()::timestamp(0), %(question_id)s, %(message)s, %(image)s)
                """
    cursor.execute(adding, {
        'user_id': data_handler_users.get_user_id(email),
        'question_id': question_id,
        'message': new_entry['message'],
        'image': new_entry.get('image', None),
        'uuid': str(uuid.uuid4()),
    })


def edit_answer(new_entry: dict):
    image = new_entry.get('image', 0)
    
    if image:
        edit_answer_receiving_image(new_entry, image)
    else:
        edit_answer_receiving_no_image(new_entry, image)


@database_common.connection_handler
def edit_answer_receiving_image(cursor: RealDictCursor, new_entry: dict, image):
    edit = """
    UPDATE answer
        SET
            message = %(new_message)s,
            image = %(new_image)s
    WHERE id = %(answer_id)s
    """
    cursor.execute(edit, {
        'new_message': new_entry['message'],
        'new_image': image,
        'answer_id': new_entry['id'],
    })


@database_common.connection_handler
def edit_answer_receiving_no_image(cursor: RealDictCursor, new_entry: dict, answer_id: int):
    edit = """
    UPDATE answer
        SET message = %(new_message)s
    WHERE id = %(answer_id)s
    """
    cursor.execute(edit, {
        'new_message': new_entry['message'],
        'answer_id': new_entry['id'],
    })


@database_common.connection_handler
def delete_answer(cursor: RealDictCursor, answer_id, path):
    try:
        delete_answer_image(answer_id, path)
    except ValueError:
        pass
    
    cursor.execute(
        sql.SQL(
            """
            DELETE FROM answer
            WHERE id = %(delete_value)s
            """
        ), {'delete_value': answer_id}
    )


def delete_answer_image(entry_id, path):
    file_list = get_image_names_for_answers(entry_id)
    
    if file_list:
        for file in file_list:
            os.unlink(os.path.join(path, file))
    
    raise ValueError


@database_common.connection_handler
def mark_answer(cursor, answer_id, status: str):
    to_modify = 1 if status == 'accepted' else 0

    cursor.execute(
        sql.SQL(
            """UPDATE {table}
                SET {col_1} = %(to_modify)s
                WHERE {col_2} = %(answer_id)s;"""
        ).format(
            table=sql.Identifier('answer'),
            col_1=sql.Identifier('accepted_by_user'),
            col_2=sql.Identifier('id'),
        ),
        {
            'to_modify': to_modify,
            'answer_id': answer_id,
        }
    )


@database_common.connection_handler
def up_vote_answer(cursor, answer_id):
    cursor.execute(
        sql.SQL("""
                UPDATE {table} 
                    SET vote_number = vote_number + 1
                WHERE id = %(entry_id)s;
                """
                ).format(table=sql.Identifier('answer')), {"entry_id": answer_id})


@database_common.connection_handler
def down_vote_answer(cursor, answer_id):
    cursor.execute(
        sql.SQL("""
                UPDATE {table}
                    SET vote_number = vote_number - 1
                WHERE id = %(entry_id)s;
                """
                ).format(table=sql.Identifier('answer')), {"entry_id": answer_id})