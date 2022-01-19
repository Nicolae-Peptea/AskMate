import bcrypt
import os
import data_handlers.data_handler_questions as data_handler_questions
import data_handlers.data_handler_answers as data_handler_answers
from flask import request


def generate_new_entry(operation, prev_entry=''):
    new_entry = dict(request.form)
    
    if is_file_in_entry():
        return generate_entry_with_image(new_entry, operation, prev_entry)
    
    return new_entry


def is_file_in_entry():
    return True if request.files['image'] else False


def generate_entry_with_image(new_entry, operation, prev_entry):
    new_file_name = generate_file_name(operation, prev_entry)
    uploaded_file = request.files['image']
    
    if uploaded_file:
        save_file(uploaded_file, new_file_name)
    new_entry['image'] = new_file_name
    
    return new_entry


def generate_file_name(operation, prev_entry):
    if operation == 'new_question':
        filename = f'question{data_handler_questions.get_last_added_question() + 1}'
    elif operation == 'new_answer':
        filename = f'answer{data_handler_answers.get_last_added_answer_id() + 1}'
    elif operation == 'edit_question':
        filename = create_img_name_when_editing(prev_entry, entry_type='question')
    elif operation == 'edit_answer':
        filename = create_img_name_when_editing(prev_entry, entry_type='answer')
    
    return filename


def create_img_name_when_editing(prev_entry: dict, entry_type: str):
    if prev_entry['image']:
        return prev_entry['image']
    
    return f"{entry_type}{prev_entry['id']}"


def save_file(uploaded_file, file_name):
    image_upload_path = os.path.join(os.path.dirname(os.path.realpath("server.py")), 'images')
    complete_path = os.path.join(image_upload_path, file_name)
    uploaded_file.save(complete_path)


def hash_password(plain_text_password):
    hashed_bytes = bcrypt.hashpw(plain_text_password.encode('utf-8'), bcrypt.gensalt())
    return hashed_bytes.decode('utf-8')


def verify_password(plain_text_password, hashed_password):
    hashed_bytes_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_text_password.encode('utf-8'), hashed_bytes_password)
