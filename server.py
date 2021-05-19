from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for, session, flash)
from dotenv import load_dotenv

import os
import data_handler_tags
import data_handler_questions
import data_handler_answers
import data_handler_comments
import data_handler_users
import psycopg2

load_dotenv()
app = Flask(__name__)
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif']
app.config['UPLOAD_PATH'] = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'images')
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


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
        filename = f'question{data_handler_questions.get_last_added_question()+1}'
    elif operation == 'new_answer':
        filename = f'answer{data_handler_answers.get_last_added_answer_id()+1}'
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
    path = app.config['UPLOAD_PATH']
    complete_path = os.path.join(path, file_name)
    uploaded_file.save(complete_path)


@app.route("/registration")
def register_user():
    return render_template('register.html')


@app.route("/registration", methods=["POST"])
def add_user():
    email = request.form.get('email')
    password = request.form.get('user_pass')
    try:
        data_handler_users.add_user(email, password)
    except psycopg2.Error:
        error = 'This user already exists'
        return render_template('register.html', error_message=error)
    session['email'] = email
    flash('You were successfully registered and automatically logged in!')
    return redirect(url_for('display_latest_questions'))


@app.route("/login")
def display_login():
    return render_template('login.html')


@app.route("/login", methods=["POST"])
def post_login():
    email = request.form.get('email')
    password = request.form.get('user_pass')
    if data_handler_users.is_valid_login(email, password):
        session['email'] = email
        flash('You were successfully logged in!')
        return redirect(url_for('display_latest_questions'))
    else:
        error_message = "Invalid login attempt"
        return render_template('login.html', error_message=error_message)


@app.route("/users")
def display_users():
    if 'email' in session:
        users_details = data_handler_users.get_users_details()
        return render_template('users.html', users_details=users_details)
    return redirect(url_for("display_login"))


@app.route("/user/<int:user_id>")
def display_user_activity(user_id):
    if 'email' in session:
        activity_details = data_handler_users.get_user_statistics(user_id)
        questions = data_handler_questions.qet_questions_by_user_id(user_id)
        answers = data_handler_answers.qet_answers_by_user_id(user_id)
        comments = data_handler_comments.get_comment_by_user_id(user_id)
        return render_template(
            'user.html',
            user_details=activity_details,
            questions=questions,
            answers=answers,
            comments=comments)
    return redirect(url_for("display_login"))


@app.route("/logout")
def logout():
    session.pop('email', None)
    return redirect(url_for('display_latest_questions'))


@app.route('/images/<filename>')
def display_image(filename):
    return send_from_directory(app.config['UPLOAD_PATH'], filename)


@app.route("/")
def display_latest_questions():
    return render_template(
        'latest_questions.html',
        questions=data_handler_questions.get_latest_questions(show=5)
    )


@app.route("/search")
def display_searched_questions():
    key_words = request.args.get('q')
    searched_questions = data_handler_questions.get_searched_questions(key_words)
    try:
        data_handler_questions.highlight_search(searched_questions, key_words)
    except ValueError:
        pass
    return render_template('latest_questions.html', questions=searched_questions)


@app.route("/list")
def display_all_questions():

    order_by = request.args.get('order_by', 'submission_time')
    direction = request.args.get('order_direction', 'desc')
    return render_template('questions.html',
                           questions=data_handler_questions.get_questions(order_by, direction),
                           request_param=request.args)


@app.route('/add-question')
def ask_question():
    if 'email' in session:
        return render_template('manipulate_question.html')
    return redirect(url_for("display_login"))


@app.route('/add-question', methods=["POST"])
def post_question():
    new_entry = generate_new_entry(operation='new_question')
    email = session.get('email')
    data_handler_questions.add_question(new_entry, email)
    question_id = data_handler_questions.get_last_added_question()
    return redirect(url_for("display_question", question_id=question_id))


@app.route("/question/<int:question_id>")
def display_question(question_id):
    data_handler_questions.update_views(question_id)
    my_question = data_handler_questions.get_question(question_id)
    answers = data_handler_answers.get_answers_for_question(question_id)
    print(answers)
    files = os.listdir(app.config['UPLOAD_PATH'])
    comments = data_handler_comments.get_comments()
    tags = data_handler_tags.get_question_tags(question_id)
    return render_template("question_page.html", my_question=my_question,
                           answers=answers, files=files,
                           comments=comments, tags=tags)


@app.route("/question/<int:question_id>/edit")
def edit_question(question_id):
    if 'email' in session:
        question = data_handler_questions.get_question(question_id)
        return render_template("manipulate_question.html", question=question)
    return redirect(url_for("display_login"))


@app.route("/question/<int:question_id>/edit", methods=["POST"])
def post_edited_question(question_id):
    question = data_handler_questions.get_question(question_id)
    new_entry = generate_new_entry(operation='edit_question', prev_entry=question)
    new_entry['id'] = question_id
    data_handler_questions.edit_question(new_entry=new_entry)
    return redirect(url_for("display_question", question_id=question_id))


@app.route('/question/<int:question_id>/delete', methods=["POST"])
def delete_question(question_id):
    if 'email' in session:
        data_handler_questions.delete_question(question_id, app.config['UPLOAD_PATH'])
        return redirect(url_for('display_all_questions'))
    return redirect(url_for("display_login"))


@app.route('/question/<int:question_id>/vote', methods=["POST"])
def vote_question(question_id):
    if 'email' in session:
        vote_type = ''.join(dict(request.form).keys())
        data_handler_questions.vote_question(question_id, 'question', vote_type)
        return redirect(url_for('display_all_questions'))
    return redirect(url_for("display_login"))


@app.route("/question/<int:question_id>/new-answer")
def answer_question(question_id):
    if 'email' in session:
        return render_template("manipulate_answer.html", question_id=question_id)
    return redirect(url_for("display_login"))


@app.route("/question/<int:question_id>/new-answer", methods=["POST"])
def post_answer(question_id):
    new_entry = generate_new_entry(operation='new_answer')
    email = session.get('email')
    data_handler_answers.add_answer(new_entry=new_entry, question_id=question_id, email=email)
    return redirect(url_for("display_question", question_id=question_id))


@app.route("/answer/<int:answer_id>/edit")
def edit_answer(answer_id):
    if 'email' in session:
        answer = data_handler_answers.get_answer(answer_id)
        return render_template('manipulate_answer.html', answer=answer)
    return redirect(url_for("display_login"))


@app.route("/answer/<int:answer_id>/edit", methods=["POST"])
def post_edited_answer(answer_id):
    answer = data_handler_answers.get_answer(answer_id)
    new_entry = generate_new_entry(operation='edit_answer', prev_entry=answer)
    new_entry['id'] = answer_id
    data_handler_answers.edit_answer(new_entry)
    return redirect(url_for("display_question", question_id=answer['question_id']))


@app.route("/answer/<int:answer_id>/accept", methods=["POST"])
def accept_answer(answer_id):
    answer = data_handler_answers.get_answer(answer_id)
    data_handler_answers.mark_answer(answer_id, 'accepted')
    return redirect(url_for("display_question", question_id=answer['question_id']))


@app.route("/answer/<int:answer_id>/remove_accept", methods=["POST"])
def mark_unaccepted(answer_id):
    answer = data_handler_answers.get_answer(answer_id)
    data_handler_answers.mark_answer(answer_id, 'unaccepted')
    return redirect(url_for("display_question", question_id=answer['question_id']))


@app.route('/answer/<int:answer_id>/delete', methods=["POST"])
def delete_answer(answer_id):
    if 'email' in session:
        question_id = data_handler_comments.get_question_id_from_answer(answer_id)
        data_handler_answers.delete_answer(answer_id, app.config['UPLOAD_PATH'])
        return redirect(url_for("display_question", question_id=question_id))
    return redirect(url_for("display_login"))


@app.route('/answer/<int:answer_id>/vote', methods=["POST"])
def vote_answer(answer_id):
    if 'email' in session:
        question_id = data_handler_comments.get_question_id_from_answer(answer_id)
        vote_type = ''.join(dict(request.form).keys())
        data_handler_questions.vote_question(answer_id, 'answer', vote_type)
        return redirect(url_for("display_question", question_id=question_id))
    return redirect(url_for("display_login"))


@app.route("/question/<int:question_id>/new-comment")
def comment_on_question(question_id):
    if 'email' in session:
        return render_template('manipulate_comment.html', question_id=question_id)
    return redirect(url_for("display_login"))


@app.route("/question/<int:question_id>/new-comment", methods=["POST"])
def post_comment_to_question(question_id):
    comment = request.form
    email = session.get('email')
    data_handler_comments.add_comment_to_question(comment, question_id, email)
    return redirect(url_for("display_question", question_id=question_id))


@app.route("/answer/<int:answer_id>/new-comment")
def comment_on_answer(answer_id):
    if 'email' in session:
        return render_template('manipulate_comment.html', answer_id=answer_id)
    return redirect(url_for("display_login"))


@app.route("/answer/<int:answer_id>/new-comment", methods=["POST"])
def post_comment_to_answer(answer_id):
    question_id = data_handler_comments.get_question_id_from_answer(answer_id)
    comment = request.form
    email = session.get('email')
    data_handler_comments.add_comment_to_answer(comment, answer_id, email)
    return redirect(url_for("display_question", question_id=question_id))


@app.route("/comment/<int:comment_id>/edit")
def edit_comment(comment_id):
    if 'email' in session:
        comment, question_id = data_handler_comments.get_comment_and_question_id(comment_id)
        return render_template('manipulate_comment.html', comment=comment)
    return redirect(url_for("display_login"))


@app.route("/comment/<int:comment_id>/edit", methods=["POST"])
def post_edited_comment(comment_id):
    comment, question_id = data_handler_comments.get_comment_and_question_id(comment_id)
    new_entry = dict(request.form)
    data_handler_comments.edit_comment(new_entry, comment_id)
    return redirect(url_for('display_question', question_id=question_id))


@app.route('/comments/<comment_id>/delete', methods=["POST"])
def delete_comment(comment_id):
    if 'email' in session:
        comment, question_id = data_handler_comments.get_comment_and_question_id(comment_id)
        data_handler_comments.delete_comment(comment_id)
        return redirect(url_for("display_question", question_id=question_id))
    return redirect(url_for("display_login"))


@app.route("/tags")
def display_tags():
    tags = data_handler_tags.get_tags()
    return render_template('tags.html', tags=tags)


@app.route("/question/<question_id>/new-tag")
def add_tag_to_question(question_id):
    if 'email' in session:
        tags = data_handler_tags.get_tags()
        return render_template('manipulate_tag.html', question_id=question_id, tags=tags)
    return redirect(url_for("display_login"))


@app.route("/question/<question_id>/new-tag", methods=["POST"])
def post_tag_to_question(question_id):
    existing_tag, new_tag = request.form.get('tags'), request.form.get('tag_name')
    data_handler_tags.add_question_tag(question_id, new_tag, existing_tag)
    return redirect(url_for("display_question", question_id=question_id))


@app.route('/question/<question_id>/tag/<tag_id>/delete', methods=["POST"])
def delete_question_tag(question_id, tag_id):
    if 'email' in session:
        data_handler_tags.delete_question_tag(question_id, tag_id)
        return redirect(url_for("display_question", question_id=question_id))
    return redirect(url_for("display_login"))


if __name__ == "__main__":
    app.run(debug=True)
