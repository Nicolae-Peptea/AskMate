from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for)
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import os
import data_handler

load_dotenv()
app = Flask(__name__)
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif']
app.config['UPLOAD_PATH'] = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'images')


def generate_entry_with_image(new_entry, path, operation, prev_entry=''):
    uploaded_file = request.files['image']
    new_file_name = generate_file_name(operation, prev_entry)
    save_file(uploaded_file, path, new_file_name)
    new_entry['image'] = new_file_name
    return new_entry


def generate_file_name(operation, prev_entry):
    if operation == 'new_question':
        filename = f'question{data_handler.get_last_added_question_id()+1}'
    elif operation == 'new_answer':
        filename = f'answer{data_handler.get_last_added_answer()+1}'
    elif operation == 'edit_question':
        if prev_entry['image']:
            filename = prev_entry['image']
        else:
            filename = f"question{prev_entry['id']}"
    elif operation == 'edit_answer':
        if prev_entry['image']:
            filename = prev_entry['image']
        else:
            filename = f"answer{prev_entry['id']}"
    return filename


def save_file(uploaded_file, path, file_name):
    complete_path = os.path.join(path, file_name)
    uploaded_file.save(complete_path)


def generate_new_entry(path, operation, prev_entry=''):
    new_entry = dict(request.form)
    if is_file_in_entry():
        entry_with_image = generate_entry_with_image(new_entry, path, operation, prev_entry)
        return entry_with_image
    return new_entry


def is_file_in_entry():
    return True if request.files else False


@app.route('/images/<filename>')
def display_image(filename):
    return send_from_directory(app.config['UPLOAD_PATH'], filename)


@app.route("/")
def display_latest_questions():
    return render_template(
        'latest_questions.html',
        questions=data_handler.get_latest_questions(show=5))


@app.route("/search")
def display_searched_questions():
    key_words=request.args.get('q')
    searched_questions=data_handler.get_searched_questions(key_words)
    try:
        data_handler.highlighted_search(searched_questions, key_words)
    except ValueError:
        pass
    return render_template(
        'latest_questions.html',
        questions=searched_questions)


@app.route("/list")
def display_all_questions():
    order_by = request.args.get('order_by', 'submission_time')
    direction = request.args.get('order_direction', 'desc')
    return render_template(
        'questions.html',
        questions=data_handler.get_questions(order_by, direction),
        request_param=request.args)


# QUESTION MANIPULATION
@app.route('/add-question')
def ask_question():
    return render_template('manipulate_question.html')


@app.route('/add-question', methods=["POST"])
def post_question():
    new_entry = generate_new_entry(app.config['UPLOAD_PATH'], operation='new_question')
    data_handler.add_question(new_entry)
    question_id = data_handler.get_last_added_question_id()
    return redirect(url_for("display_question", question_id=question_id))


@app.route("/question/<int:question_id>")
def display_question(question_id):
    data_handler.update_views(question_id)
    my_question = data_handler.get_question(question_id)
    answers = data_handler.get_answers_for_question(question_id)
    files = os.listdir(app.config['UPLOAD_PATH'])
    comments = data_handler.get_comments()
    tags = data_handler.get_question_tags(question_id)
    return render_template("question_page.html",
                           my_question=my_question,
                           answers=answers,
                           files=files,
                           comments=comments, 
                           tags=tags)


@app.route("/question/<int:question_id>/edit")
def edit_question(question_id):
    question = data_handler.get_question(question_id)
    return render_template(
        "manipulate_question.html",
        question=question
    )


@app.route("/question/<int:question_id>/edit", methods=["POST"])
def post_edited_question(question_id):
    question = data_handler.get_question(question_id)
    new_entry = generate_new_entry(app.config['UPLOAD_PATH'], operation='edit_question', prev_entry=question)
    data_handler.edit_question(new_entry=new_entry, question_id=question_id)
    return redirect(url_for("display_question", question_id=question_id))


@app.route('/question/<int:question_id>/delete', methods=["POST"])
def delete_question(question_id):
    data_handler.delete_question(question_id, app.config['UPLOAD_PATH'])
    return redirect(url_for('display_all_questions'))


@app.route('/question/<int:question_id>/vote', methods=["POST"])
def vote_question(question_id):
    vote_type = ''.join(dict(request.form).keys())
    data_handler.vote_question(question_id, 'question', vote_type)
    return redirect(url_for('display_all_questions'))


# ANSWER MANIPULATION
@app.route("/question/<int:question_id>/new-answer")
def answer_question(question_id):
    return render_template("manipulate_answer.html", question_id=question_id)


@app.route("/question/<int:question_id>/new-answer", methods=["POST"])
def post_answer(question_id):
    new_entry = generate_new_entry(app.config['UPLOAD_PATH'], operation='new_answer')
    data_handler.add_answer(new_entry=new_entry, question_id=question_id)
    return redirect(url_for("display_question", question_id=question_id))


@app.route("/answer/<int:answer_id>/edit")
def edit_answer(answer_id):
    answer = data_handler.get_answer(answer_id)
    return render_template('manipulate_answer.html', answer=answer)


@app.route("/answer/<int:answer_id>/edit", methods=["POST"])
def post_edited_answer(answer_id):
    answer = data_handler.get_answer(answer_id)
    new_entry = generate_new_entry(app.config['UPLOAD_PATH'], operation='edit_answer', prev_entry=answer)
    data_handler.edit_answer(new_entry=new_entry, answer_id=answer_id)
    return redirect(url_for("display_question", question_id=answer['question_id']))


@app.route('/answer/<int:answer_id>/delete', methods=["POST"])
def delete_answer(answer_id):
    question_id = data_handler.get_question_id_from_answer(answer_id)
    data_handler.delete_answer(answer_id, app.config['UPLOAD_PATH'])
    return redirect(url_for("display_question", question_id=question_id))


@app.route('/answer/<int:answer_id>/vote', methods=["POST"])
def vote_answer(answer_id):
    question_id = data_handler.get_question_id_from_answer(answer_id)
    vote_type = ''.join(dict(request.form).keys())
    data_handler.vote_question(answer_id, 'answer', vote_type)
    return redirect(url_for("display_question", question_id=question_id))


# COMMENT MANIPULATION
@app.route("/question/<int:question_id>/new-comment")
def comment_on_question(question_id):
    return render_template('manipulate_comment.html', question_id=question_id)


@app.route("/question/<int:question_id>/new-comment", methods=["POST"])
def post_comment_to_question(question_id):
    comment = request.form
    data_handler.add_comment_to_question(comment, question_id)
    return redirect(url_for("display_question", question_id=question_id))


@app.route("/answer/<int:answer_id>/new-comment")
def comment_on_answer(answer_id):
    return render_template('manipulate_comment.html', answer_id=answer_id)


@app.route("/answer/<int:answer_id>/new-comment", methods=["POST"])
def post_comment_to_answer(answer_id):
    question_id = data_handler.get_question_id_from_answer(answer_id)
    comment = request.form
    data_handler.add_comment_to_answer(comment, answer_id)
    return redirect(url_for("display_question", question_id=question_id))


@app.route("/comment/<int:comment_id>/edit")
def edit_comment(comment_id):
    comment, question_id = data_handler.get_comment_and_question_id(comment_id)
    return render_template('manipulate_comment.html', comment=comment)


@app.route("/comment/<int:comment_id>/edit", methods=["POST"])
def post_edited_comment(comment_id):
    comment, question_id = data_handler.get_comment_and_question_id(comment_id)
    new_entry = dict(request.form)
    data_handler.edit_comment(new_entry, comment_id)
    return redirect(url_for('display_question', question_id=question_id))


@app.route('/comments/<comment_id>/delete', methods=["POST"])
def delete_comment(comment_id):
    comment, question_id = data_handler.get_comment_and_question_id(comment_id)
    data_handler.delete_comment(comment_id)
    return redirect(url_for("display_question", question_id=question_id))


# TAG MANIPULATION
@app.route("/question/<question_id>/new-tag")
def add_tag_to_question(question_id):
    question_tags = data_handler.get_question_tags(question_id)
    return render_template(
        'manipulate_tag.html', question_id=question_id, question_tags=question_tags)


@app.route("/question/<question_id>/new-tag", methods=["POST"])
def post_tag_to_question(question_id):
    existing_tag, new_tag  = request.form.get('tags'), request.form.get('tag_name')
    print(existing_tag, new_tag)
    data_handler.add_question_tag(question_id, new_tag, existing_tag)
    return redirect(url_for("display_question", question_id=question_id))


@app.route('/question/<question_id>/tag/<tag_id>/delete', methods=["POST"])
def delete_question_tag(question_id, tag_id):
    data_handler.delete_question_tag(question_id, tag_id)
    return redirect(url_for("display_question", question_id=question_id))


if __name__ == "__main__":
    app.run(debug=True)
