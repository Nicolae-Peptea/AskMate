import os
import re
import database_common
from psycopg2 import sql
from psycopg2.extras import RealDictCursor


# GET
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
def get_question_id_from_answer(cursor: RealDictCursor, answer_id: int):
    query = """
    SELECT question_id FROM answer
    WHERE id = %(answer_id)s
    """
    cursor.execute(query, {'answer_id': answer_id})
    return cursor.fetchone()['question_id']


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


# DELETE
@database_common.connection_handler
def delete_comment(cursor, comment_id):
    delete = "DELETE FROM comment WHERE id = %(comment_id)s"
    cursor.execute(delete, {'comment_id': comment_id})


@database_common.connection_handler
def delete_question_tag(cursor, question_id, tag_id):
    delete = """
    DELETE FROM question_tag 
        WHERE 
            question_id = %(question_id)s AND tag_id = %(tag_id)s
    """
    cursor.execute(delete, {'question_id': question_id, 'tag_id': tag_id})
