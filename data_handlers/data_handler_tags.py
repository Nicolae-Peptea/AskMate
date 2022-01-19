import data_handlers.database_common as database_common
from psycopg2.extras import RealDictCursor


@database_common.connection_handler
def get_tags(cursor: RealDictCursor):
    query = """SELECT * FROM tag"""
    cursor.execute(query)
    
    return [dict(value) for value in cursor.fetchall()]


@database_common.connection_handler
def get_tags_and_questions_count(cursor: RealDictCursor):
    query = """
        SELECT
            tag.id,
            tag.name as name,
            COUNT(question_tag.question_id) as questions
        FROM tag
        JOIN question_tag
            ON question_tag.tag_id = tag.id
        GROUP BY
            tag.name, tag.id;"""
    cursor.execute(query)
    
    return [dict(value) for value in cursor.fetchall()]


@database_common.connection_handler
def get_question_tags(cursor: RealDictCursor, question_id: int):
    query = """
    SELECT * FROM question_tag, tag
    WHERE question_id = %(question_id)s
    AND tag.id = question_tag.tag_id
    """
    cursor.execute(query, {'question_id': question_id})
    
    return [dict(value) for value in cursor.fetchall()]


def add_question_tag(question_id: int, new_tag, existing_tag):
    if new_tag:
        tag_question_receiving_new_tag(question_id, new_tag)
    else:
        tag_question_receiving_existing_tag(question_id, existing_tag)


def tag_question_receiving_new_tag(question_id: int, new_tag):
    add_new_tag(new_tag)
    tag_id = generate_tag_id_by_name(new_tag)
    attach_tag_to_question(question_id, tag_id)


def tag_question_receiving_existing_tag(question_id: int, existing_tag):
    tag_id = generate_tag_id_by_name(existing_tag)
    attach_tag_to_question(question_id, tag_id)


@database_common.connection_handler
def add_new_tag(cursor: RealDictCursor, new_tag):
    query = """INSERT INTO tag ("name")
                VALUES (%(name)s);"""
    cursor.execute(query, {'name': new_tag})


@database_common.connection_handler
def generate_tag_id_by_name(cursor: RealDictCursor, tag_name):
    query = """SELECT id FROM tag
                WHERE name=%(name)s;"""
    cursor.execute(query, {'name': tag_name})
    
    return cursor.fetchone()['id']


@database_common.connection_handler
def attach_tag_to_question(cursor: RealDictCursor, question_id: int, tag_id):
    query = """INSERT INTO question_tag ("question_id", "tag_id")
                VALUES (%(question_id)s, %(tag_id)s)"""
    cursor.execute(query, {
        'question_id': question_id,
        'tag_id': tag_id
    })


@database_common.connection_handler
def delete_question_tag(cursor, question_id, tag_id):
    delete = """
    DELETE FROM question_tag
        WHERE
            question_id = %(question_id)s AND tag_id = %(tag_id)s
    """
    cursor.execute(delete, {'question_id': question_id, 'tag_id': tag_id})
