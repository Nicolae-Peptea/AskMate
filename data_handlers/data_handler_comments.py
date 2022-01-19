import data_handlers.database_common as database_common
import data_handlers.data_handler_users as data_handler_users
import uuid

from psycopg2.extras import RealDictCursor
from psycopg2 import sql


@database_common.connection_handler
def get_question_id_from_answer(cursor: RealDictCursor, answer_id: int):
    query = """
    SELECT question_id FROM answer
    WHERE id = %(answer_id)s
    """
    cursor.execute(query, {'answer_id': answer_id})
    return cursor.fetchone()['question_id']


@database_common.connection_handler
def get_comments(cursor: RealDictCursor):
    query = """SELECT c.id, c.user_id, c.question_id, c.answer_id, c.message,
                        c.submission_time, c.edited_count, u.email
                FROM comment c
                JOIN users u on u.id = c.user_id"""
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_comment(cursor: RealDictCursor, comment_id: int):
    query = """SELECT * FROM comment
                WHERE id = %(comment_id)s"""
    cursor.execute(query, {"comment_id": comment_id})
    return dict(cursor.fetchone())


def get_comment_and_question_id(comment_id: int):
    comment = get_comment(comment_id)

    if comment['question_id']:
        question_id = comment['question_id']
    elif comment['answer_id']:
        question_id = get_question_id_from_answer(comment['answer_id'])
    
    return comment, question_id


@database_common.connection_handler
def get_comment_by_user_id(cursor, user_id: int):
    cursor.execute(
        sql.SQL(
            """
            SELECT c.message, question.id FROM question
            JOIN comment c ON question.id = c.question_id
            WHERE c.user_id = %(user_id)s
            UNION
            SELECT c.message, answer.question_id FROM answer
            JOIN comment c ON answer.id = c.answer_id
            WHERE c.user_id = %(user_id)s;
            """
        ),
        {"user_id": user_id}
    )

    return cursor.fetchall()


@database_common.connection_handler
def add_comment_to_question(cursor: RealDictCursor, new_entry: dict, question_id: int, email: str):
    adding = """INSERT INTO comment (uuid, user_id, submission_time, question_id, message)
                    VALUES (%(uuid)s, %(user_id)s, now()::timestamp(0), %(question_id)s, %(message)s)
                    """
    cursor.execute(adding, {
        'user_id': data_handler_users.get_user_id(email),
        'question_id': question_id,
        'message': new_entry['message'],
        'uuid': str(uuid.uuid4()),
    })


@database_common.connection_handler
def add_comment_to_answer(cursor: RealDictCursor, new_entry: dict, answer_id: int, email: str):
    adding = """INSERT INTO comment (uuid, user_id, submission_time, answer_id, message)
                    VALUES (%(uuid)s, %(user_id)s, now()::timestamp(0), %(answer_id)s, %(message)s)
                    """
    cursor.execute(adding, {
        'user_id': data_handler_users.get_user_id(email),
        'answer_id': answer_id,
        'message': new_entry['message'],
        'uuid': str(uuid.uuid4()),
    })


@database_common.connection_handler
def edit_comment(cursor: RealDictCursor, new_entry: dict, comment_id: int):
    edit = """
    UPDATE comment
        SET message = %(new_message)s,
            submission_time = now()::timestamp(0),
            edited_count = edited_count + 1
    WHERE id = %(comment_id)s
    """
    cursor.execute(edit, {
        'new_message': new_entry['message'],
        'comment_id': comment_id
    })


@database_common.connection_handler
def delete_comment(cursor, comment_id):
    delete = "DELETE FROM comment WHERE id = %(comment_id)s"
    cursor.execute(delete, {'comment_id': comment_id})
