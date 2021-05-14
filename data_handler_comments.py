import database_common
from psycopg2.extras import RealDictCursor


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
    query = "SELECT * FROM comment"
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
def add_comment_to_question(cursor: RealDictCursor, new_entry: dict, question_id: int):
    adding = """INSERT INTO comment ("submission_time","question_id","message","edited_count")
                    VALUES (now()::timestamp(0), %(question_id)s, %(message)s, 0)
                    """
    cursor.execute(adding, {
        'question_id': question_id,
        'message': new_entry['message'],
    })


@database_common.connection_handler
def add_comment_to_answer(cursor: RealDictCursor, new_entry: dict, answer_id: int):
    adding = """INSERT INTO comment ("submission_time","answer_id","message","edited_count")
                    VALUES (now()::timestamp(0), %(answer_id)s, %(message)s, 0)
                    """
    cursor.execute(adding, {
        'answer_id': answer_id,
        'message': new_entry['message'],
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