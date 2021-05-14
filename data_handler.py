import os
import re
import database_common
from psycopg2 import sql
from psycopg2.extras import RealDictCursor


# GET







@database_common.connection_handler
def get_question_tags(cursor: RealDictCursor, question_id: int):
    query = """
    SELECT * FROM question_tag, tag
    WHERE question_id = %(question_id)s
    AND tag.id = question_tag.tag_id
    """
    cursor.execute(query, {'question_id': question_id})
    return [dict(value) for value in cursor.fetchall()]


# ADD


@database_common.connection_handler
def add_question_tag(cursor: RealDictCursor, question_id: int, new_tag, existing_tag):
    if new_tag:
        add_new_tag = """INSERT INTO tag ("name")
                    VALUES (%(name)s);
                    SELECT id FROM tag
                    WHERE name=%(name)s;"""
        cursor.execute(add_new_tag, {'name': new_tag})
        tag_id = cursor.fetchone()['id']
        attach_tag_to_question="""
        INSERT INTO question_tag ("question_id", "tag_id")
                    VALUES (%(question_id)s, %(tag_id)s)"""
        cursor.execute(attach_tag_to_question, {
            'question_id': question_id,
            'tag_id': tag_id
        })
    else:
        select_tag = """SELECT id FROM tag WHERE name=%(name)s;"""
        cursor.execute(select_tag, {'name': existing_tag})
        tag_id = cursor.fetchone()['id']
        attach_tag_to_question="""
        INSERT INTO question_tag ("question_id", "tag_id")
                    VALUES (%(question_id)s, %(tag_id)s)"""
        cursor.execute(attach_tag_to_question, {
            'question_id': question_id,
            'tag_id': tag_id
        })


# EDIT



@database_common.connection_handler
def delete_question_tag(cursor, question_id, tag_id):
    delete = """
    DELETE FROM question_tag 
        WHERE 
            question_id = %(question_id)s AND tag_id = %(tag_id)s
    """
    cursor.execute(delete, {'question_id': question_id, 'tag_id': tag_id})
